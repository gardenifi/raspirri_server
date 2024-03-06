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

import random
from raspirri.server.const import ARCH

if ARCH == "arm":
    import dbus
    import pytest
    from raspirri.ble.wifi import WifiCharacteristic, WifiNetworksService

    class TestWifiCharacteristic:
        """Wifi Characteristic Test Class"""

        def test_instantiation_success(self):
            """WifiCharacteristic object can be instantiated successfully."""
            wifi_service = WifiNetworksService(1111)
            wifi_characteristic = WifiCharacteristic(wifi_service)
            assert isinstance(wifi_characteristic, WifiCharacteristic)

        def test_write_value_parse_success(self):
            """WriteValue method can parse JSON data successfully."""
            wifi_service = WifiNetworksService(2222)
            wifi_characteristic = WifiCharacteristic(wifi_service)
            with pytest.raises(
                ValueError, match="Command 'sudo nmcli device wifi connect my_ssid password my_wifi_key' returned non-zero exit status 10."
            ):
                wifi_characteristic.WriteValue(['{"ssid": "my_ssid", "wifi_key": "my_wifi_key"}'], None)

        def test_read_value_return_list(self):
            """ReadValue method can return a list of dbus.Byte objects."""
            wifi_service = WifiNetworksService(3333)
            wifi_characteristic = WifiCharacteristic(wifi_service)
            values = wifi_characteristic.ReadValue(None)
            assert isinstance(values, list)
            assert all(isinstance(value, dbus.Byte) for value in values)

        def test_write_value_invalid_json(self):
            """WriteValue method can handle invalid JSON data."""
            wifi_service = WifiNetworksService(4444)
            wifi_characteristic = WifiCharacteristic(wifi_service)
            with pytest.raises(ValueError, match="Expecting value: .*"):
                wifi_characteristic.WriteValue(["invalid_json"], None)

        def test_write_value_missing_data(self):
            """WriteValue method can handle missing JSON data."""
            wifi_service = WifiNetworksService(5555)
            wifi_characteristic = WifiCharacteristic(wifi_service)
            with pytest.raises(ValueError, match="Missing data! You provided only: .*"):
                wifi_characteristic.WriteValue(['{"ssid": "my_ssid"}'], None)

        @pytest.mark.parametrize(
            ("page", "service", "expected_result"),
            (
                (
                    "0",
                    random.randint(0, 1000),
                    '{"hw_id": "10000000f7f23721", "mqtt_broker": {"host": "localhost", "port": 1883, \
"user": "user", "pass": "pass"}, "page": 0, "nets": [{"id": 1, "ssid": "Network1"}, {"id": 2, "ssid": "Network2"}], "pages": 1}',
                ),
            ),
        )
        def test_write_value_page(self, page, service, expected_result):
            """WriteValue method with page argument."""
            wifi_service = WifiNetworksService(service)
            wifi_characteristic = WifiCharacteristic(wifi_service)
            wifi_characteristic.WriteValue(['{"page": "' + page + '"}'], None)
            byte_list = wifi_characteristic.ReadValue(None)
            # Convert the array of integers to a string
            actual_result = "".join(map(chr, byte_list))
            actual_result = actual_result.replace("'", '"')
            assert actual_result == expected_result

        def test_read_value_invalid_page_set(self):
            """ReadValue method can handle invalid page_set values."""
            wifi_service = WifiNetworksService(7777)
            wifi_characteristic = WifiCharacteristic(wifi_service)
            wifi_characteristic._page_set = "invalid_page"  # pylint: disable=protected-access
            with pytest.raises(ValueError, match="'>' not supported between instances of 'str' and 'int'"):
                wifi_characteristic.ReadValue(None)
