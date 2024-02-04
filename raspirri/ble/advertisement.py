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

from loguru import logger
from raspirri.server.const import ARCH

if ARCH == "arm":
    import dbus
    import dbus.service  # pylint: disable=import-error,useless-import-alias

    from raspirri.ble.bletools import BleTools
    from raspirri.ble.exceptions import InvalidArgsException
    from raspirri.ble.common import BLUEZ_SERVICE_NAME, LE_ADVERTISING_MANAGER_IFACE, LE_ADVERTISEMENT_IFACE, DBUS_PROP_IFACE

    class Advertisement(dbus.service.Object):  # pylint: disable=too-many-instance-attributes
        """Bluetooth Advertisement module."""

        PATH_BASE = "/org/bluez/raspirri/advertisement"

        # Nine arguments are reasonable in this case.

        def __init__(self, index, advertising_type):
            self.path = f"{self.PATH_BASE}{index}"
            self.ble_tools = BleTools()
            self.bus = self.ble_tools.get_bus()
            self.ad_type = advertising_type
            self.local_name = None
            self.service_uuids = None
            self.solicit_uuids = None
            self.manufacturer_data = None
            self.service_data = None
            self.include_tx_power = None
            super().__init__(self.bus, self.path)

        def get_properties(self):
            """Bluetooth Advertisement module properties."""

            properties = {}
            properties["Type"] = self.ad_type

            if self.local_name is not None:
                properties["LocalName"] = dbus.String(self.local_name)

            if self.service_uuids is not None:
                properties["ServiceUUIDs"] = dbus.Array(self.service_uuids, signature="s")
            if self.solicit_uuids is not None:
                properties["SolicitUUIDs"] = dbus.Array(self.solicit_uuids, signature="s")
            if self.manufacturer_data is not None:
                properties["ManufacturerData"] = dbus.Dictionary(self.manufacturer_data, signature="qv")

            if self.service_data is not None:
                properties["ServiceData"] = dbus.Dictionary(self.service_data, signature="sv")
            if self.include_tx_power is not None:
                properties["IncludeTxPower"] = dbus.Boolean(self.include_tx_power)

            if self.local_name is not None:
                properties["LocalName"] = dbus.String(self.local_name)

            return {LE_ADVERTISEMENT_IFACE: properties}

        def get_path(self):
            """path propertie."""
            return dbus.ObjectPath(self.path)

        def add_service_uuid(self, uuid):
            """add service uuid property."""
            if self.service_uuids is None:
                self.service_uuids = []
            self.service_uuids.append(uuid)

        def add_solicit_uuid(self, uuid):
            """add solicit uuid property."""
            if self.solicit_uuids is None:
                self.solicit_uuids = []
            self.solicit_uuids.append(uuid)

        def add_manufacturer_data(self, manuf_code, data):
            """add manufacturer data property."""
            if self.manufacturer_data is None:
                self.manufacturer_data = dbus.Dictionary({}, signature="qv")
            self.manufacturer_data[manuf_code] = dbus.Array(data, signature="y")

        def add_service_data(self, uuid, data):
            """add service data property."""
            if self.service_data is None:
                self.service_data = dbus.Dictionary({}, signature="sv")
            self.service_data[uuid] = dbus.Array(data, signature="y")

        def add_local_name(self, name):
            """add local name property."""
            if self.local_name is None:
                self.local_name = ""
            self.local_name = dbus.String(name)

        @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
        def GetAll(self, interface):  # pylint: disable=invalid-name
            """get all properties."""
            if interface != LE_ADVERTISEMENT_IFACE:
                raise InvalidArgsException()

            return self.get_properties()[LE_ADVERTISEMENT_IFACE]

        @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature="", out_signature="")
        def Release(self):  # pylint: disable=invalid-name
            """release ble."""
            logger.info(f"{self.path}: Released!")

        def register_ad_callback(self):
            """register ad callback."""
            logger.info(f"{self.path}: GATT advertisement registered")

        def register_ad_error_callback(self):
            """register ad error callback."""
            logger.error(f"{self.path}: Failed to register GATT advertisement")

        def register(self):
            """register."""
            logger.info(f"Bus found: {self.bus}")
            adapter = self.ble_tools.find_adapter()
            logger.info(f"Adapter found: {adapter}")

            ad_manager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, adapter), LE_ADVERTISING_MANAGER_IFACE)
            logger.info(f"ad_manager found: {ad_manager}")

            ad_manager.RegisterAdvertisement(
                self.get_path(), {}, reply_handler=self.register_ad_callback, error_handler=self.register_ad_error_callback
            )
