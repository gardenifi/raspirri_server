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

from itertools import count
from loguru import logger
from app.raspi.const import ARCH

if ARCH == "arm":
    import dbus  # pylint: disable=import-error,useless-import-alias
    import dbus.mainloop.glib  # pylint: disable=import-error,useless-import-alias
    import dbus.exceptions  # pylint: disable=import-error,useless-import-alias
    import dbus.service

    from array import array
    from app.ble.bletools import BleTools
    from app.ble.exceptions import InvalidArgsException, NotSupportedException, NotPermittedException

    try:
        from gi.repository import GObject
    except ImportError:
        import gobject as GObject

    BLUEZ_SERVICE_NAME = "org.bluez"
    GATT_MANAGER_IFACE = "org.bluez.GattManager1"
    DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
    DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"
    GATT_SERVICE_IFACE = "org.bluez.GattService1"
    GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
    GATT_DESC_IFACE = "org.bluez.GattDescriptor1"

    BLUEZ_SERVICE_NAME = "org.bluez"
    GATT_MANAGER_IFACE = "org.bluez.GattManager1"
    DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"

    class Application(dbus.service.Object):
        """Bluetooth module."""

        def __init__(self, path="/"):
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            self.mainloop = GObject.MainLoop()
            self.ble_tools = BleTools()
            self.bus = self.ble_tools.get_bus()
            self.path = path
            self.services = []
            self.next_index = 0
            dbus.service.Object.__init__(self, self.bus, self.path)

        def get_path(self):
            """Bluetooth module."""
            return dbus.ObjectPath(self.path)

        def add_service(self, service):
            """Bluetooth module."""
            self.services.append(service)

        @dbus.service.method(DBUS_OM_IFACE, out_signature="a{oa{sa{sv}}}")
        def GetManagedObjects(self):  # pylint: disable=invalid-name
            """Bluetooth module."""
            response = {}

            for service in self.services:
                response[service.get_path()] = service.get_properties()
                chrcs = service.get_characteristics()
                for chrc in chrcs:
                    response[chrc.get_path()] = chrc.get_properties()
                    descs = chrc.get_descriptors()
                    for desc in descs:
                        response[desc.get_path()] = desc.get_properties()

            return response

        def register_app_callback(self):
            """Bluetooth module."""
            logger.info(f"GATT application registered. Path: {self.path}")

        def register_app_error_callback(self, error):
            """Bluetooth module."""
            logger.info(f"{self.path}: Failed to register application: {error}")

        def register(self):
            """Bluetooth module."""
            adapter = self.ble_tools.find_adapter()
            logger.info(f"{self.path}: Adapter: {adapter}")

            service_manager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, adapter), GATT_MANAGER_IFACE)
            logger.info(f"{self.path}: Service Manager: {service_manager}")

            service_manager.RegisterApplication(
                self.get_path(), {}, reply_handler=self.register_app_callback, error_handler=self.register_app_error_callback
            )
            logger.info(f"{self.path}: Service Manager Registered...")

        def run(self):
            """Bluetooth module."""
            self.mainloop.run()

        def quit(self):
            """Bluetooth module."""
            logger.info("\nGATT application terminated")
            self.mainloop.quit()

    class Service(dbus.service.Object):
        """Bluetooth module."""

        PATH_BASE = "/org/bluez/raspirri/service"

        def __init__(self, index, uuid, primary):
            self.ble_tools = BleTools()
            self.bus = self.ble_tools.get_bus()
            self.path = self.PATH_BASE + str(index)
            self.uuid = uuid
            self.primary = primary
            self.characteristics = set()
            self.index_counter = count()
            dbus.service.Object.__init__(self, self.bus, self.path)

        def get_properties(self):
            """Bluetooth module."""
            return {
                GATT_SERVICE_IFACE: {
                    "UUID": self.uuid,
                    "Primary": self.primary,
                    "Characteristics": dbus.Array(self.get_characteristic_paths(), signature="o"),
                }
            }

        def get_path(self):
            """Bluetooth module."""
            return dbus.ObjectPath(self.path)

        def add_characteristic(self, characteristic):
            """Bluetooth module."""
            self.characteristics.add(characteristic)

        def get_characteristic_paths(self):
            """Bluetooth module."""
            return [chrc.get_path() for chrc in self.characteristics]

        def get_characteristics(self):
            """Bluetooth module."""
            return self.characteristics

        def get_bus(self):
            """Bluetooth module."""
            return self.bus

        def get_next_index(self):
            """Bluetooth module."""
            return next(self.index_counter)

        @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
        def GetAll(self, interface):  # pylint: disable=invalid-name
            """Bluetooth module."""
            if interface != GATT_SERVICE_IFACE:
                raise InvalidArgsException()

            return self.get_properties()[GATT_SERVICE_IFACE]

    class Characteristic(dbus.service.Object):
        """
        org.bluez.GattCharacteristic1 interface implementation
        """

        def __init__(self, uuid, flags, service):
            index = service.get_next_index()
            self.path = service.path + "/char" + str(index)
            self.bus = service.get_bus()
            self.uuid = uuid
            self.service = service
            self.flags = flags
            self.descriptors = []
            self.next_index = 0
            dbus.service.Object.__init__(self, self.bus, self.path)

        def get_properties(self):
            """Bluetooth module."""

            return {
                GATT_CHRC_IFACE: {
                    "Service": self.service.get_path(),
                    "UUID": self.uuid,
                    "Flags": self.flags,
                    "Descriptors": dbus.Array(self.get_descriptor_paths(), signature="o"),
                }
            }

        def get_path(self):
            """Bluetooth module."""
            return dbus.ObjectPath(self.path)

        def add_descriptor(self, descriptor):
            """Bluetooth module."""
            self.descriptors.append(descriptor)

        def get_descriptor_paths(self):
            """Bluetooth module."""
            result = []
            for desc in self.descriptors:
                result.append(desc.get_path())
            return result

        def get_descriptors(self):
            """Bluetooth module."""
            return self.descriptors

        @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
        def GetAll(self, interface):  # pylint: disable=invalid-name
            """Bluetooth module."""
            if interface != GATT_CHRC_IFACE:
                raise InvalidArgsException()

            return self.get_properties()[GATT_CHRC_IFACE]

        @dbus.service.method(GATT_CHRC_IFACE, in_signature="a{sv}", out_signature="ay")
        def ReadValue(self, options):  # pylint: disable=invalid-name
            """Bluetooth module."""
            raise NotSupportedException("ReadValue is not supported for this characteristic.")

        @dbus.service.method(GATT_CHRC_IFACE, in_signature="aya{sv}")
        def WriteValue(self, values, options):  # pylint: disable=invalid-name
            """Bluetooth module."""
            raise NotSupportedException("WriteValue is not supported for this characteristic.")

        @dbus.service.method(GATT_CHRC_IFACE)
        def StartNotify(self):  # pylint: disable=invalid-name
            """Bluetooth module."""
            raise NotSupportedException("StartNotify is not supported for this characteristic.")

        @dbus.service.method(GATT_CHRC_IFACE)
        def StopNotify(self):  # pylint: disable=invalid-name
            """Bluetooth module."""
            raise NotSupportedException("StopNotify is not supported for this characteristic.")

        @dbus.service.signal(DBUS_PROP_IFACE, signature="sa{sv}as")
        def PropertiesChanged(self, interface, changed, invalidated):  # pylint: disable=invalid-name
            """Bluetooth module."""
            logger.info(
                f"{self.path}: Default propertiesChanged called, returning, \
                {interface}, {changed}, {invalidated}"
            )

        def get_bus(self):
            """Bluetooth module."""
            return self.bus

        def get_next_index(self):
            """Bluetooth module."""
            idx = self.next_index
            self.next_index += 1
            return idx

        def add_timeout(self, timeout, callback):
            """Bluetooth module."""
            logger.info(f"{self.path}: Default add_timeout called")
            GObject.timeout_add(timeout, callback)

    class Descriptor(dbus.service.Object):
        """Bluetooth module."""

        def __init__(self, uuid, flags, characteristic):
            index = characteristic.get_next_index()
            self.path = characteristic.path + "/desc" + str(index)
            self.uuid = uuid
            self.flags = flags
            self.characteristic = characteristic
            self.bus = characteristic.get_bus()
            dbus.service.Object.__init__(self, self.bus, self.path)

        def get_properties(self):
            """Bluetooth module."""
            return {
                GATT_DESC_IFACE: {
                    "Characteristic": self.characteristic.get_path(),
                    "UUID": self.uuid,
                    "Flags": self.flags,
                }
            }

        def get_path(self):
            """Bluetooth module."""
            return dbus.ObjectPath(self.path)

        @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
        def GetAll(self, interface):  # pylint: disable=invalid-name
            """Bluetooth module."""
            if interface != GATT_DESC_IFACE:
                raise InvalidArgsException()

            return self.get_properties()[GATT_DESC_IFACE]

        @dbus.service.method(GATT_DESC_IFACE, in_signature="a{sv}", out_signature="ay")
        def ReadValue(self, options):  # pylint: disable=invalid-name
            """Bluetooth module."""
            raise NotSupportedException()

        @dbus.service.method(GATT_DESC_IFACE, in_signature="aya{sv}")
        def WriteValue(self, values, options):  # pylint: disable=invalid-name
            """Bluetooth module."""
            raise NotSupportedException()

    class CharacteristicUserDescriptionDescriptor(Descriptor):
        """Bluetooth module."""

        CUD_UUID = "2901"

        def __init__(self, characteristic):
            self.writable = "writable-auxiliaries" in characteristic.flags
            self.value = array("B", b"This is a characteristic for testing")
            self.value = self.value.tolist()
            Descriptor.__init__(self, self.CUD_UUID, ["read", "write"], characteristic)

        def ReadValue(self, options):  # pylint: disable=invalid-name
            """Bluetooth module."""
            logger.info(f"Read value: {self.value}")
            return self.value

        def WriteValue(self, values, options):  # pylint: disable=invalid-name
            """Bluetooth module."""
            logger.info(f"Write value: {self.value}")
            if not self.writable:
                raise NotPermittedException()
            self.value = values
