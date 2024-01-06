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
    import dbus

    from app.ble.wifi import WifiNetworksService
    from app.ble.wifi import ConnectivityCharacteristic
    from app.raspi.helpers import Helpers
    from app.raspi.mqtt import Mqtt

    class TestReadValue:
        """ReadValue Test Class"""

        def test_connected_status_true_mqtt_running(self, mocker):
            """Returns a list with one element, a dbus.Byte object with value b"1",
            if the connected status is True and the MQTT thread is running"""

            # Initialize the class object
            service = WifiNetworksService(11111)
            characteristic = ConnectivityCharacteristic(service)

            # Mock the necessary dependencies
            mocker.patch.object(Helpers, "__new__")
            mocker.patch.object(Mqtt, "__new__")

            # Set up the mock return values
            Helpers().is_connected_to_inet.return_value = True
            Mqtt().is_running.return_value = True

            # Invoke the method under test
            options = None
            result = characteristic.ReadValue(options)

            # Assert the result
            assert len(result) == 1
            assert isinstance(result[0], dbus.Byte)
            assert result[0] == dbus.Byte(b"1")

        def test_connected_status_false(self, mocker):
            """Returns a list with one element,
            a dbus.Byte object with value b"0", if the connected status is False"""

            # Initialize the class object
            service = WifiNetworksService(22222)
            characteristic = ConnectivityCharacteristic(service)

            # Mock the necessary dependencies
            mocker.patch.object(Helpers, "__new__")

            # Set up the mock return value
            Helpers().is_connected_to_inet = False

            # Invoke the method under test
            options = None
            result = characteristic.ReadValue(options)

            # Assert the result
            assert len(result) == 1
            assert isinstance(result[0], dbus.Byte)
            assert result[0] == dbus.Byte(b"0")

        def test_connected_status_true_mqtt_not_running(self, mocker):
            """Returns a list with one element, a dbus.Byte object
            with value b"1", if the connected status is True and the MQTT thread is not running"""

            # Initialize the class object
            service = WifiNetworksService(44444)
            characteristic = ConnectivityCharacteristic(service)

            # Mock the necessary dependencies
            mocker.patch.object(Helpers, "__new__")
            mocker.patch.object(Mqtt, "__new__")

            # Set up the mock return values
            Helpers().is_connected_to_inet = True
            Mqtt().is_running.return_value = False

            # Invoke the method under test
            options = None
            result = characteristic.ReadValue(options)

            # Assert the result
            assert len(result) == 1
            assert isinstance(result[0], dbus.Byte)
            assert result[0] == dbus.Byte(b"1")

        def test_do_not_start_mqtt_thread_from_ble_module(self, mocker):
            """If the connected status is True and the
            MQTT thread is not running, starts the MQTT thread"""
            # Initialize the class object
            service = WifiNetworksService(55555)
            characteristic = ConnectivityCharacteristic(service)

            # Mock the necessary dependencies
            mocker.patch.object(Helpers, "__new__")
            mocker.patch.object(Mqtt, "__new__")

            # Set up the mock return values
            Helpers().is_connected_to_inet.return_value = True
            Mqtt().is_running.return_value = False

            # Invoke the method under test
            options = None
            characteristic.ReadValue(options)

            # Assert that the MQTT thread was not started
            Mqtt().start_mqtt_thread.assert_not_called()

        def test_do_not_start_mqtt_thread(self, mocker):
            """If the connected status is False, does not start the MQTT thread"""
            # Initialize the class object
            service = WifiNetworksService(66666)
            characteristic = ConnectivityCharacteristic(service)

            # Mock the necessary dependencies
            mocker.patch.object(Helpers, "__new__")
            mocker.patch.object(Mqtt, "__new__")

            # Set up the mock return values
            Helpers().is_connected_to_inet.return_value = False

            # Invoke the method under test
            options = None
            characteristic.ReadValue(options)

            # Assert that the MQTT thread was not started
            Mqtt().start_mqtt_thread.assert_not_called()

        def test_connected_status_none(self, mocker):
            """If the connected status is None, returns an empty list"""
            # Initialize the class object
            service = WifiNetworksService(77777)
            characteristic = ConnectivityCharacteristic(service)

            # Mock the necessary dependencies
            mocker.patch.object(Helpers, "__new__")

            # Set up the mock return value
            Helpers().is_connected_to_inet = False

            # Invoke the method under test
            result = characteristic.ReadValue(None)

            # Assert the result
            assert result[0] == dbus.Byte(b"0")
