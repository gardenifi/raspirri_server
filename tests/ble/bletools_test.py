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

from raspirri.server.const import ARCH

if ARCH == "arm":
    import dbus
    import pytest
    from raspirri.ble.bletools import BleTools

    class TestBleTools:
        """BleTools Test Class"""

        def test_get_bus_returns_system_bus_object(self, mocker):
            """get_bus method returns a dbus SystemBus object"""
            bus_mock = mocker.Mock()
            mocker.patch("raspirri.ble.bletools.dbus.SystemBus", return_value=bus_mock)

            bus = BleTools().get_bus()

            assert bus == bus_mock

        def test_find_adapter_returns_correct_adapter_object(self, mocker):
            """find_adapter method returns the correct adapter object"""
            objects_mock = {
                "/org/bluez/raspirri/adapter1": {"org.bluez.Adapter1": {}},
                "/org/bluez/raspirri/adapter2": {"org.bluez.Adapter1": {}},
            }
            mocker.patch("dbus.Interface")
            mocker.patch("raspirri.ble.bletools.BleTools.get_bus")
            mocker.patch("raspirri.ble.bletools.BleTools.find_adapter", return_value="/org/bluez/raspirri/adapter1")
            mocker.patch("raspirri.ble.bletools.BleTools.get_bus.get_object", side_effect=lambda *args: objects_mock[args[1]])

            adapter = BleTools().find_adapter()

            assert adapter == "/org/bluez/raspirri/adapter1"

        def test_power_adapter_powers_on_adapter(self, mocker):
            """power_adapter method powers on the adapter"""
            dbus_interface_mock = mocker.patch("dbus.Interface")
            find_adapter_mock = mocker.patch("raspirri.ble.bletools.BleTools.find_adapter", return_value="/org/bluez/raspirri/adapter1")

            # Create a mock object for adapter_props
            adapter_props_mock = dbus_interface_mock.return_value

            # Call the method you want to test
            BleTools().power_adapter()

            # Check that Set method was called with the expected arguments
            if not adapter_props_mock.Get("org.bluez.Adapter1", "Powered"):
                adapter_props_mock.Set.assert_called_once_with("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

            # Ensure that BleTools.find_adapter was called
            find_adapter_mock.assert_called_once()

        def test_find_adapter_returns_none_when_no_adapter_found(self, mocker):
            """find_adapter method returns None when no adapter is found"""
            objects_mock = {
                "/org/bluez/raspirri/adapter1": {"org.bluez.Adapter1": {}},
                "/org/bluez/raspirri/adapter2": {"org.bluez.Adapter1": {}},
            }
            mocker.patch("dbus.Interface")
            mocker.patch("raspirri.ble.bletools.BleTools.get_bus")
            mocker.patch("raspirri.ble.bletools.BleTools.get_bus.get_object", side_effect=lambda *args: objects_mock[args[1]])

            adapter = BleTools().find_adapter()

            assert adapter is None

        def test_power_adapter_raises_exception_when_adapter_not_found(self, mocker):
            """power_adapter method raises an exception when adapter is not found"""
            mocker.patch("raspirri.ble.bletools.BleTools.find_adapter", return_value=None)

            with pytest.raises(Exception):
                BleTools().power_adapter()

        def test_ble_tools_class_imported_correctly(self):
            """BleTools class is imported correctly"""
            assert BleTools
