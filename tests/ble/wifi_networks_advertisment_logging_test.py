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
    import unittest
    import random
    from loguru import logger
    from app.ble.wifi import WifiNetworksAdvertisement

    class TestWifiNetworksAdvertisement(unittest.TestCase):
        """Wifi Networks Advertisement Test Class"""

        def setUp(self):
            # Create a list to capture log records
            self.log_records = []

            # Patch the logger to use a custom sink for testing
            def testing_sink(record):
                self.log_records.append(record)

            logger.add(testing_sink, level="INFO", catch=True)

            # Initialize adv here or remove if not needed in setUp
            self.adv = WifiNetworksAdvertisement(random.randint(22222, 100000))

        def tearDown(self):
            # Remove the testing sink from the logger
            logger.remove()
            yield self.adv

        def test_advertisement_registered_logging(self):
            """Advertisement registered! Listening for ble requests..."""
            # Use the adv object created by the fixture
            self.adv.register_ad_callback()
            self.assertTrue(any("WifiNetworksAdvertisement initialized with index: 5"), self.log_records)
            self.assertTrue(any("advertising type: 'peripheral', local name: 'raspirriv1', and include_tx_power: True."), self.log_records)
            self.assertTrue(any("GATT advertisement registered for WifiNetworksAdvertisement\n"), self.log_records)

        def test_advertisement_registered_error_logging(self):
            """Advertisement registered! Listening for ble requests..."""
            # Use the adv object created by the fixture
            self.adv.register_ad_error_callback()
            self.assertTrue(any("Failed to register GATT advertisement for WifiNetworksAdvertisement\n"), self.log_records)
