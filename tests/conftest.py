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
from loguru import logger
import pytest
from raspirri.server.const import ARCH


@pytest.fixture(scope="function", autouse=True)
def setup():
    """Setup fixture: runs before every function execution"""
    logger.info("Conftest Setup")


if ARCH == "arm":
    import dbus
    from gi.repository import GObject
    from raspirri.ble.service import Service
    from raspirri.ble.wifi import WifiNetworksAdvertisement

    RANDOM_SVC_INDEX = []

    # Set up the main loop as a fixture
    @pytest.fixture(scope="class", autouse=True)
    def setup_main_loop():
        """Setup main loop fixture: runs before every class execution"""
        GObject.threads_init()
        loop = GObject.MainLoop()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        yield loop
        loop.quit()

    @pytest.fixture(scope="class")
    def setup_service():
        """Setup service fixture: runs before every class execution"""
        # Perform setup operations for the service here
        random_index = random.randint(0, 100)
        while random_index in RANDOM_SVC_INDEX:
            random_index = random.randint(0, 100)
        RANDOM_SVC_INDEX.append(random_index)
        service = Service(random_index, "1234", True)
        yield service
        # Perform teardown operations for the service here, if necessary
        service = None

    @pytest.fixture(scope="class")
    def setup_advertisment():
        """Setup advertisment fixture: runs before every class execution"""
        adv = WifiNetworksAdvertisement(0)
        yield adv
