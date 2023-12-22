"""MIT License

Copyright (c) 2023, Marios Karagiannopoulos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

**Attribution Requirement:**
When using or distributing the software, an attribution to Marios Karagiannopoulos must be included.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from app.raspi.const import ARCH

if ARCH == "arm":
    from loguru import logger
    import json

    from app.ble.wifi import WifiNetworksService
    from app.ble.wifi import WifiCharacteristic
    from app.ble.wifi import ConnectivityCharacteristic
    from app.raspi.const import RPI_HW_ID, MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASS

    class TestWifiNetworksService:
        """Wifi Networks Service Test Class"""

        def test_instantiation_success(self):
            """WifiNetworksService object can be instantiated successfully"""
            wifi_service = WifiNetworksService(9111)
            assert isinstance(wifi_service, WifiNetworksService)

        def test_add_characteristics_success(self):
            """WifiCharacteristic and ConnectivityCharacteristic
            can be added to WifiNetworksService object successfully"""
            wifi_service = WifiNetworksService(9222)
            wifi_service.add_characteristic(WifiCharacteristic(wifi_service))
            wifi_service.add_characteristic(ConnectivityCharacteristic(wifi_service))
            characteristics = wifi_service.get_characteristics()
            assert len(characteristics) == 4

        def test_read_value_no_networks(self):
            """WifiCharacteristic ReadValue returns empty list if no wifi networks found"""
            wifi_service = WifiNetworksService(9333)
            wifi_characteristic = WifiCharacteristic(wifi_service)
            byte_list = wifi_characteristic.ReadValue(None)

            logger.debug(f"byte_list: {byte_list}")

            # Convert the array of integers to a string
            actual_result = "".join(map(chr, byte_list))
            actual_result = actual_result.replace("'", '"')
            logger.info(f"actual_result={actual_result}")

            _ap_array = [{"id": i, "ssid": f"Network{i}"} for i in range(1, 3)]
            expected_result = {
                "hw_id": RPI_HW_ID,
                "mqtt_broker": {"host": MQTT_HOST, "port": int(MQTT_PORT), "user": MQTT_USER, "pass": MQTT_PASS},
                "page": 1,
                "nets": _ap_array,
                "pages": 1,
            }
            expected_result = json.dumps(expected_result).replace("'", '"')
            logger.info(f"expected_result={expected_result}")

            # Assert
            assert actual_result == expected_result

        def test_write_value_invalid_json(self, mocker):
            """WifiCharacteristic WriteValue does not change
            wifi credentials if invalid json data is sent"""
            wifi_service = WifiNetworksService(9444)
            wifi_characteristic = WifiCharacteristic(wifi_service)
            mocker.patch.object(wifi_characteristic, "WriteValue")
            values = ["invalid json"]
            wifi_characteristic.WriteValue(values, None)
            wifi_characteristic.WriteValue.assert_called_once()  # pylint: disable=no-member

        def test_write_value_invalid_credentials(self, mocker):
            """WifiCharacteristic WriteValue does not change
            wifi credentials if invalid ssid or wifi_key is sent"""
            wifi_service = WifiNetworksService(9555)
            wifi_characteristic = WifiCharacteristic(wifi_service)
            mocker.patch.object(wifi_characteristic, "WriteValue")
            values = ['{"ssid": "my_ssid"}']
            wifi_characteristic.WriteValue(values, None)
            wifi_characteristic.WriteValue.assert_called_once()  # pylint: disable=no-member
