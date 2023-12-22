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

from app.raspi.const import ARCH

if ARCH == "arm":
    import dbus

    from app.ble.common import (
        BLUEZ_SERVICE_NAME,
        LE_ADVERTISING_MANAGER_IFACE,
        DBUS_OM_IFACE,
        DBUS_PROP_IFACE,
    )

    class BleTools:
        """Bluetooth module."""

        def __init__(self):
            """Initialize BleTools."""
            self.bus = dbus.SystemBus()

        def get_bus(self):
            """Get bus."""
            return self.bus

        def find_adapter(self, return_all=False):
            """Find adapter."""
            remote_om = dbus.Interface(self.get_bus().get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE)
            objects = remote_om.GetManagedObjects()
            matching_adapters = []

            for item, props in objects.items():
                if LE_ADVERTISING_MANAGER_IFACE in props:
                    matching_adapters.append(item)

            if return_all:
                return matching_adapters
            return matching_adapters[0] if matching_adapters else None

        def power_adapter(self):
            """Power adapter."""
            adapter = self.find_adapter()

            adapter_props = dbus.Interface(self.get_bus().get_object(BLUEZ_SERVICE_NAME, adapter), DBUS_PROP_IFACE)
            if not adapter_props.Get("org.bluez.Adapter1", "Powered"):
                adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))
