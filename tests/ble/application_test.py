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
    from raspirri.ble.service import Application
    from raspirri.ble.service import Characteristic
    from raspirri.ble.service import Descriptor

    APP = Application()

    class TestApplication:
        """Application Test Class"""

        def test_instantiation_success(self):
            """Application object can be instantiated successfully"""
            assert isinstance(APP, Application)
            managed_objects = APP.GetManagedObjects()
            assert isinstance(managed_objects, dict)
            assert len(managed_objects) == 0

        def test_add_service_success(self, setup_service):
            """Services can be added to the Application object successfully"""
            APP.add_service(setup_service)
            assert len(APP.services) == 1
            assert APP.services[0] == setup_service

        def test_get_managed_objects_success(self, setup_service):
            """GetManagedObjects method returns a dictionary of managed objects"""
            characteristic = Characteristic("5678", ["read"], setup_service)
            descriptor = Descriptor("abcd", [], characteristic)
            setup_service.add_characteristic(characteristic)
            characteristic.add_descriptor(descriptor)
            APP.add_service(setup_service)
            managed_objects = APP.GetManagedObjects()
            assert isinstance(managed_objects, dict)
            assert len(managed_objects) == 3

        def test_get_managed_objects_empty(self, setup_service):
            """GetManagedObjects method returns an empty dictionary"""
            characteristic = Characteristic("5678", ["read"], setup_service)
            descriptor = Descriptor("abcd", [], characteristic)
            setup_service.add_characteristic(characteristic)
            characteristic.add_descriptor(descriptor)
            APP.add_service(setup_service)
            APP.services = []
            managed_objects = APP.GetManagedObjects()
            assert isinstance(managed_objects, dict)
            assert len(managed_objects) == 0
