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
    from unittest.mock import MagicMock

    import dbus
    import pytest

    from raspirri.ble.service import Characteristic
    from raspirri.ble.exceptions import InvalidArgsException
    from raspirri.ble.exceptions import NotSupportedException
    from raspirri.ble.service import GATT_CHRC_IFACE

    class TestCharacteristic:
        """Characteristic Test Class"""

        def test_create_instance_with_valid_arguments(self, setup_service):
            """can create a new instance of Characteristic with valid arguments"""
            characteristic = Characteristic("1234", ["read", "write"], setup_service)
            assert characteristic.uuid == "1234"
            assert characteristic.flags == ["read", "write"]
            assert characteristic.service == setup_service
            assert not characteristic.descriptors
            assert characteristic.next_index == 0

        def test_add_descriptor(self, setup_service):
            """can add a new descriptor to the characteristic"""
            characteristic = Characteristic("1234", ["read", "write"], setup_service)
            descriptor = MagicMock()
            characteristic.add_descriptor(descriptor)
            assert characteristic.descriptors == [descriptor]

        def test_get_path(self, setup_service):
            """can get the path of the characteristic"""
            characteristic = Characteristic("1234", ["read", "write"], setup_service)
            assert characteristic.get_path() == dbus.ObjectPath(characteristic.path)

        def test_get_all_with_invalid_interface(self, setup_service):
            """raises InvalidArgsException if GetAll is called with an invalid interface"""
            characteristic = Characteristic("1234", ["read", "write"], setup_service)
            with pytest.raises(InvalidArgsException):
                characteristic.GetAll("invalid_interface")

        def test_read_value(self, setup_service):
            """raises NotSupportedException if ReadValue is called"""
            characteristic = Characteristic("1234", ["read", "write"], setup_service)
            with pytest.raises(NotSupportedException):
                characteristic.ReadValue({})

        def test_write_value(self, setup_service):
            """raises NotSupportedException if WriteValue is called"""
            characteristic = Characteristic("1234", ["read", "write"], setup_service)
            with pytest.raises(NotSupportedException):
                characteristic.WriteValue([1, 2, 3], {})

        def test_get_descriptors(self, setup_service):
            """can get the descriptors of the characteristic"""
            characteristic = Characteristic("1234", ["read", "write"], setup_service)
            descriptor1 = MagicMock()
            descriptor2 = MagicMock()
            characteristic.descriptors = [descriptor1, descriptor2]
            assert characteristic.get_descriptors() == [descriptor1, descriptor2]

        def test_get_properties(self, setup_service):
            """can get the descriptors of the characteristic"""
            characteristic = Characteristic("1234", ["read", "write"], setup_service)
            descriptor1 = MagicMock()
            descriptor2 = MagicMock()
            characteristic.descriptors = [descriptor1, descriptor2]
            expected_properties = {
                GATT_CHRC_IFACE: {
                    "Service": setup_service.get_path(),
                    "UUID": "1234",
                    "Flags": ["read", "write"],
                    "Descriptors": dbus.Array([descriptor1.get_path(), descriptor2.get_path()], signature="o"),
                }
            }
            assert characteristic.get_properties() == expected_properties

        def test_get_bus(self, setup_service):
            """can get the bus of the characteristic"""
            bus = setup_service.get_bus()
            characteristic = Characteristic("1234", ["read", "write"], setup_service)
            assert characteristic.get_bus() == bus
