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

    class TestWifiNetworksAdvertisement:
        """Wifi Networks Advertisement Test Class"""

        def test_initialization_completed(self, setup_advertisment):
            """Initialization completed"""
            adv = setup_advertisment
            assert adv.local_name == "raspirriv1"
            assert adv.include_tx_power is True

        def test_advertisement_registered(self, mocker, setup_advertisment):
            """Advertisement registered! Listening for ble requests..."""
            adv = setup_advertisment
            mocker.patch.object(adv, "register_ad_callback")
            mocker.patch.object(adv, "register_ad_error_callback")
            mocker.patch.object(adv, "register")
            adv.register_ad_callback()
            adv.register_ad_callback.assert_called_once()
            adv.register_ad_error_callback.assert_not_called()

        def test_wifi_networks_service_registered(self, mocker, setup_advertisment):
            """WifiNetworksService registered!"""
            adv = setup_advertisment
            mocker.patch.object(adv, "register")
            app = mocker.Mock()
            app.add_service = mocker.Mock()
            adv.add_local_name = mocker.Mock()
            adv.include_tx_power = True
            adv.register.return_value = app
            adv.register()
            app.add_service()
            app.add_service.assert_called_once()

        def test_failed_to_register_gatt_advertisement(self, mocker, setup_advertisment):
            """Failed to register GATT advertisement"""
            adv = setup_advertisment
            mocker.patch.object(adv, "register_ad_callback")
            mocker.patch.object(adv, "register_ad_error_callback")
            mocker.patch.object(adv, "register")
            adv.register_ad_error_callback()
            adv.register_ad_callback.assert_not_called()

        def test_gatt_advertisement_registered(self, mocker, setup_advertisment):
            """GATT advertisement registered"""
            adv = setup_advertisment
            mocker.patch.object(adv, "register_ad_callback")
            mocker.patch.object(adv, "register_ad_error_callback")
            mocker.patch.object(adv, "register")
            adv.register_ad_callback()
            adv.register_ad_error_callback.assert_not_called()

        def test_type_property(self, setup_advertisment):
            """Type property"""
            adv = setup_advertisment
            assert adv.ad_type == "peripheral"
