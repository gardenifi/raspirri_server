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
    import dbus

    from app.ble.advertisement import Advertisement
    from app.ble.common import LE_ADVERTISEMENT_IFACE
    from app.ble.common import BLUEZ_SERVICE_NAME

    # Set up the GLib main loop for D-Bus
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Create a D-Bus connection
    bus = dbus.SessionBus()

    class TestAdvertisement:
        """Unit Test Advertisment Class."""

        def test_initialization(self):
            """Advertisement object can be initialized with an index and advertising type"""

            advertising_type = "peripheral"

            advertisement = Advertisement(1, advertising_type)

            assert advertisement.path == "/org/bluez/raspirri/advertisement1"
            assert advertisement.ble_tools is not None
            assert advertisement.bus is not None
            assert advertisement.ad_type == "peripheral"
            assert advertisement.local_name is None
            assert advertisement.service_uuids is None
            assert advertisement.solicit_uuids is None
            assert advertisement.manufacturer_data is None
            assert advertisement.service_data is None
            assert advertisement.include_tx_power is None

        def test_add_properties(self):
            """Properties can be added to the advertisement object
            (local name, service UUIDs, solicit UUIDs,
            manufacturer data, service data, include TX power)
            """

            advertising_type = "peripheral"

            advertisement = Advertisement(2, advertising_type)

            advertisement.add_service_uuid("1234")
            advertisement.add_local_name("MyDevice")
            advertisement.add_manufacturer_data(123, [1, 2, 3])
            advertisement.add_service_data("5678", [4, 5, 6])
            advertisement.include_tx_power = True

            properties = advertisement.get_properties()[LE_ADVERTISEMENT_IFACE]

            assert properties["ServiceUUIDs"] == dbus.Array(["1234"], signature="s")
            assert properties["LocalName"] == dbus.String("MyDevice")
            assert properties["ManufacturerData"] == dbus.Dictionary({123: dbus.Array([1, 2, 3], signature="y")}, signature="qv")
            assert properties["ServiceData"] == dbus.Dictionary({"5678": dbus.Array([4, 5, 6], signature="y")}, signature="sv")
            assert properties["IncludeTxPower"] == dbus.Boolean(True)

        def test_register(self, mocker):
            """The advertisement object can be registered"""
            advertising_type = "peripheral"

            advertisement = Advertisement(3, advertising_type)

            mocker.patch.object(advertisement.ble_tools, "find_adapter", return_value="adapter")

            # Mock the dbus.SystemBus() and related methods
            mocker.patch("dbus.SystemBus", autospec=True)
            mock_system_bus = mocker.MagicMock()
            mocker.patch.object(advertisement, "bus", mock_system_bus)

            # Mock the get_object method to return a valid D-Bus object
            mock_adapter = mocker.MagicMock()
            mock_system_bus.get_object.return_value = mock_adapter

            # Mock the get_interface method to return a valid interface
            mock_ad_manager = mocker.MagicMock()
            mock_system_bus.get_object.return_value = mock_ad_manager

            advertisement.register()

            advertisement.ble_tools.find_adapter.assert_called_once()  # pylint: disable=no-member
            mock_system_bus.get_object.assert_called_once_with(BLUEZ_SERVICE_NAME, "adapter")

        def test_none_properties_set(self):
            """None of the properties are set"""
            advertising_type = "peripheral"

            advertisement = Advertisement(4, advertising_type)

            properties = advertisement.get_properties()[LE_ADVERTISEMENT_IFACE]

            assert properties["Type"] == advertising_type
            assert "LocalName" not in properties
            assert "ServiceUUIDs" not in properties
            assert "SolicitUUIDs" not in properties
            assert "ManufacturerData" not in properties
            assert "ServiceData" not in properties
            assert "IncludeTxPower" not in properties

        def test_some_properties_set(self):
            """Only some of the properties are set"""
            advertising_type = "peripheral"

            advertisement = Advertisement(5, advertising_type)

            advertisement.add_service_uuid("1234")
            advertisement.add_manufacturer_data(123, [1, 2, 3])
            advertisement.include_tx_power = True

            properties = advertisement.get_properties()[LE_ADVERTISEMENT_IFACE]

            assert properties["Type"] == advertising_type
            assert properties["ServiceUUIDs"] == dbus.Array(["1234"], signature="s")
            assert "LocalName" not in properties
            assert "SolicitUUIDs" not in properties
            assert properties["ManufacturerData"] == dbus.Dictionary({123: dbus.Array([1, 2, 3], signature="y")}, signature="qv")
            assert "ServiceData" not in properties
            assert properties["IncludeTxPower"] == dbus.Boolean(True)
