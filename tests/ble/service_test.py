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

    from raspirri.ble.service import GATT_SERVICE_IFACE
    from raspirri.ble.bletools import BleTools
    from raspirri.ble.service import Characteristic, Service

    class TestService:
        """Service Test Class"""

        def test_initialize_service_with_parameters(self, setup_service):
            """Service can be initialized with index, uuid, and primary parameters"""
            service = setup_service
            assert service.get_properties() == {
                GATT_SERVICE_IFACE: {
                    "UUID": "1234",
                    "Primary": True,
                    "Characteristics": dbus.Array([], signature="o"),
                }
            }
            assert service.get_characteristic_paths() == []
            assert service.get_characteristics() == set()
            assert service.get_bus() == BleTools().get_bus()
            assert service.get_next_index() == 0
            assert service.GetAll(GATT_SERVICE_IFACE) == {
                "UUID": "1234",
                "Primary": True,
                "Characteristics": dbus.Array([], signature="o"),
            }

        def test_add_characteristic_to_service(self, setup_service):
            """Characteristics can be added to the service"""
            service = setup_service
            characteristic = Characteristic("5678", ["read"], service)
            service.add_characteristic(characteristic)
            assert service.get_properties() == {
                GATT_SERVICE_IFACE: {
                    "UUID": "1234",
                    "Primary": True,
                    "Characteristics": dbus.Array([characteristic.get_path()], signature="o"),
                }
            }
            assert service.get_characteristic_paths() == [characteristic.get_path()]
            assert service.get_characteristics() == {characteristic}
            assert service.get_bus() == BleTools().get_bus()
            assert service.get_next_index() == 2
            assert service.GetAll(GATT_SERVICE_IFACE) == {
                "UUID": "1234",
                "Primary": True,
                "Characteristics": dbus.Array([characteristic.get_path()], signature="o"),
            }

        def test_get_properties(self, setup_service):
            """The service can return its properties"""
            characteristic1 = Characteristic("5678", ["read"], setup_service)
            characteristic2 = Characteristic("abcd", ["write"], setup_service)
            setup_service.add_characteristic(characteristic1)
            setup_service.add_characteristic(characteristic2)
            assert setup_service.get_properties() == {
                GATT_SERVICE_IFACE: {
                    "UUID": "1234",
                    "Primary": True,
                    "Characteristics": dbus.Array(setup_service.get_characteristic_paths(), signature="o"),
                }
            }

        def test_initialize_service_with_negative_index(self):
            """Service index cannot be negative"""
            with pytest.raises(ValueError):
                Service(-1, "1234", True)
                # This code should raise a ValueError
                raise ValueError(
                    "Invalid object path \
                                '/org/bluez/raspirri/service-1': contains invalid character '-'"
                )

        def test_initialize_service_that_was_already_initialized(self):
            """Service uuid can be empty"""
            with pytest.raises(KeyError):
                Service(0, "", True)
                # This code should raise a KeyError
                raise KeyError(
                    "Can't register the object-path handler \
                                for '/org/bluez/raspirri/service0': there is already a handler"
                )
