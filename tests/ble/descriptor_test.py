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

    from raspirri.ble.service import Characteristic
    from raspirri.ble.service import Descriptor
    from raspirri.ble.service import GATT_DESC_IFACE
    from raspirri.ble.exceptions import InvalidArgsException
    from raspirri.ble.exceptions import NotSupportedException

    class TestDescriptor:
        """Descriptor Test Class"""

        def test_initialization(self, setup_service):
            """Descriptor object can be initialized with a UUID,
            flags, and a characteristic object."""
            service = setup_service
            characteristic = Characteristic("1234", ["read"], service)
            descriptor = Descriptor("abcd", [], characteristic)
            assert descriptor.uuid == "abcd"
            assert descriptor.flags == []
            assert descriptor.characteristic == characteristic

        def test_get_properties(self, setup_service):
            """Descriptor object can return its properties,
            including its UUID, flags, and the path of its characteristic."""
            service = setup_service
            characteristic = Characteristic("1234", ["read"], service)
            descriptor = Descriptor("abcd", [], characteristic)
            properties = descriptor.get_properties()
            assert properties == {
                GATT_DESC_IFACE: {
                    "Characteristic": descriptor.characteristic.get_path(),
                    "UUID": descriptor.uuid,
                    "Flags": descriptor.flags,
                }
            }

        def test_get_path(self, setup_service):
            """Descriptor object can return its path."""
            service = setup_service
            characteristic = Characteristic("1234", ["read"], service)
            descriptor = Descriptor("abcd", [], characteristic)
            path = descriptor.get_path()
            assert path == dbus.ObjectPath(descriptor.path)

        def test_get_all_invalid_interface(self, setup_service):
            """Descriptor object raises an InvalidArgsException
            if GetAll method is called with an interface other than GATT_DESC_IFACE."""
            service = setup_service
            characteristic = Characteristic("1234", ["read"], service)
            descriptor = Descriptor("abcd", [], characteristic)
            with pytest.raises(InvalidArgsException):
                descriptor.GetAll("invalid_interface")

        def test_read_value_not_supported(self, setup_service):
            """Descriptor object raises a NotSupportedException if ReadValue method is called."""
            service = setup_service
            characteristic = Characteristic("1234", ["read"], service)
            descriptor = Descriptor("abcd", [], characteristic)
            with pytest.raises(NotSupportedException):
                descriptor.ReadValue({})

        def test_write_value_not_supported(self, setup_service):
            """Descriptor object raises a NotSupportedException if WriteValue method is called."""
            service = setup_service
            characteristic = Characteristic("1234", ["read"], service)
            descriptor = Descriptor("abcd", [], characteristic)
            with pytest.raises(NotSupportedException):
                descriptor.WriteValue([1, 2, 3], {})

        def test_get_all_properties(self, setup_service):
            """Descriptor object can get all of its properties."""
            service = setup_service
            characteristic = Characteristic("1234", ["read"], service)
            descriptor = Descriptor("abcd", [], characteristic)
            properties = descriptor.get_properties()
            assert properties == {"org.bluez.GattDescriptor1": {"Characteristic": characteristic.get_path(), "UUID": "abcd", "Flags": []}}

        def test_read_value(self, setup_service):
            """Descriptor object can read its value."""
            service = setup_service
            characteristic = Characteristic("1234", ["read"], service)
            descriptor = Descriptor("abcd", [], characteristic)
            with pytest.raises(NotSupportedException):
                descriptor.ReadValue({})

        def test_write_value(self, setup_service):
            """Descriptor object can write its value."""
            service = setup_service
            characteristic = Characteristic("1234", ["read"], service)
            descriptor = Descriptor("abcd", [], characteristic)
            with pytest.raises(NotSupportedException):
                descriptor.WriteValue([], {})
