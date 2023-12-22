"""Copyright (c) 2019, Douglas Otwell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from loguru import logger
import dbus  # pylint: disable=import-error,useless-import-alias

from dbus.exceptions import DBusException

from app.raspi.helpers import Helpers
from app.raspi.services import Services
from app.raspi.mqtt import Mqtt
from app.ble.advertisement import Advertisement
from app.ble.service import Application, Service, Characteristic

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000


class WifiNetworksAdvertisement(Advertisement):  # pylint: disable=too-few-public-methods
    """Bluetooth module."""

    def __init__(self, index):
        super().__init__(index, "peripheral")
        self.add_local_name("raspirriv1")
        self.include_tx_power = True
        logger.info(
            f"WifiNetworksAdvertisement initialized with index: {index}, \
            advertising type: 'peripheral', local name: 'raspirriv1', and include_tx_power: True."
        )

    def register_ad_callback(self):
        """Register ad callback."""
        logger.info(f"{self.path}: GATT advertisement registered for WifiNetworksAdvertisement")

    def register_ad_error_callback(self):
        """Register ad error callback."""
        logger.error(f"{self.path}: Failed to register GATT advertisement for WifiNetworksAdvertisement")


class WifiNetworksService(Service):  # pylint: disable=too-few-public-methods
    """Bluetooth module."""

    SVC_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, index, page=1, connected=0):
        self._page = page
        self._connected = connected
        super().__init__(index, self.SVC_UUID, True)
        self._add_characteristics()
        self._log_characteristics_added()

    def _add_characteristics(self):
        self.add_characteristic(WifiCharacteristic(self))
        self.add_characteristic(ConnectivityCharacteristic(self))

    def _log_characteristics_added(self):
        logger.info("Adding characteristics completed.")


class WifiCharacteristic(Characteristic):
    """Bluetooth module."""

    WIFI_CHARACTERISTIC_UUID = "00000003-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        super().__init__(self.WIFI_CHARACTERISTIC_UUID, ["read", "write", "write-without-response"], service)
        self._page_set = 1
        self._refresh_set = False
        self._services = Services()
        logger.info("Adding WifiCharacteristic completed.")

    def WriteValue(self, values, options):  # pylint: disable=unused-argument,invalid-name
        """Bluetooth module."""
        command = "".join(str(value) for value in values)
        logger.debug(f"command: {command}")
        try:
            json_data = json.loads(command)
            if json_data.get("page"):
                self._page_set = int(json_data["page"])
                logger.debug(f"Page set: {self._page_set}")
            elif json_data.get("refresh"):
                value = json_data["refresh"]
                if value.lower() == "true":
                    self._refresh_set = True
                else:
                    self._refresh_set = False
                logger.debug(f"refresh: {self._refresh_set}")
            elif json_data.get("ssid") and json_data.get("wifi_key"):
                connected = Helpers().store_wpa_ssid_key(json_data["ssid"], json_data["wifi_key"])
                logger.info(f"Wifi changed: {json_data}. Connected: {connected}")
            else:
                raise ValueError(f"Missing data! You provided only: {json_data}")
        except json.JSONDecodeError as exception:
            logger.error(f"JSONDecodeError: {exception}")
            raise ValueError(f"{exception}") from exception
        except Exception as exception:
            logger.error(f"Error: {exception}")
            raise ValueError(f"{exception}") from exception

    def ReadValue(self, options):  # pylint: disable=unused-argument,invalid-name
        """Bluetooth module."""
        values = []
        try:
            logger.debug(f"page set earlier: {self._page_set}")
            wifi_networks = self._services.discover_wifi_networks(1, self._page_set, self._refresh_set)
            logger.debug(f"wifi_networks: {wifi_networks}")
            if not wifi_networks:
                wifi_networks = "No wifi networks identified!"
            for char in str(wifi_networks):
                values.append(dbus.Byte(char.encode()))
        except DBusException as exception:
            logger.error(f"DBusException: {exception}")
            raise ValueError(f"{exception}") from exception
        except Exception as exception:
            logger.error(f"Error: {exception}")
            raise ValueError(f"{exception}") from exception
        return values


class ConnectivityCharacteristic(Characteristic):  # pylint: disable=too-few-public-methods
    """Bluetooth module."""

    CONN_CHARACTERISTIC_UUID = "00000004-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        super().__init__(self.CONN_CHARACTERISTIC_UUID, ["read"], service)

    def ReadValue(self, options):  # pylint: disable=invalid-name,unused-argument
        """Bluetooth module."""
        values = []
        logger.debug(f"connected: {Helpers().is_connected_to_inet}")
        if Helpers().is_connected_to_inet:
            values.append(dbus.Byte(b"1"))
            if not Mqtt().is_running():
                Mqtt().start_mqtt_thread()
        else:
            values.append(dbus.Byte(b"0"))
            logger.debug(f"values: {values}")
        return values


def init_ble():
    """Bluetooth module."""
    logger.info("Initializing BLE module...")

    app = Application()
    logger.info(f"app path: {app.get_path()}")
    logger.info(f"app services: {app.services}")

    wifi_service_index = 0

    app.add_service(WifiNetworksService(wifi_service_index))
    try:
        app.register()
        logger.info("WifiNetworksService registered!")
    except Exception as exception:
        logger.error(f"Error registering WifiNetworksService: {exception}")
        app.quit()

    adv = WifiNetworksAdvertisement(wifi_service_index)
    try:
        adv.register()
        logger.info("Advertisement registered! Listening for ble requests...")
    except Exception as exception:
        logger.error(f"Error registering Advertisement: {exception}")
        app.quit()

    try:
        logger.info("Advertisement app will run...")
        app.run()
        logger.info("Advertisement app completed successfully.")
    except KeyboardInterrupt as exception:
        logger.error(f"Error: {exception}")
        app.quit()
    except Exception as exception:
        logger.error(f"Error: {exception}")
        # Handle the exception here, e.g. log the error or perform any necessary cleanup
        # ...
        raise  # Re-raise the exception to propagate it further if needed
