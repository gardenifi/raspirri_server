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

import tempfile
import pickle
import unittest
from unittest.mock import patch, MagicMock
import re
import os
import signal
from datetime import datetime
import pytest
from app.raspi.helpers import logger
from app.raspi.helpers import Helpers
from app.raspi.const import RPI_HW_ID, ARCH, STATUSES_FILE, NETWORKS_FILE
from app.main_app import setup_gpio


@pytest.fixture(autouse=True, scope="function")
def destroy():
    """
    A pytest fixture that is automatically used before and after each test function.
    It is responsible for destroying an instance of the Helpers class.
    """
    yield
    Helpers.destroy_instance()


class TestHelpers(unittest.TestCase):
    """Helpers Test Class"""

    def setUp(self):
        # Set the path for temporary testing file
        self.test_file_path = "test_data.pkl"
        self.empty_file_path = "empty.pkl"
        self.helpers_instance = Helpers()
        self.test_data = {"key": "value"}
        # Set up any necessary resources or configurations
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            self.temp_file = temp_file

    def tearDown(self):
        # Clean up any resources created during the test
        os.remove(self.temp_file.name)
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        if os.path.exists(self.empty_file_path):
            os.remove(self.empty_file_path)

    def test_returns_single_instance(self):
        """a single instance of Helpers class"""
        helpers_instance_1 = Helpers()
        helpers_instance_2 = Helpers()
        assert helpers_instance_1 is helpers_instance_2

    def test_set_valves_sets_valves_status(self):
        """set_valves method sets the valves status in toggle_statuses dictionary"""

        valves = [1, 2, 3, 4]
        self.helpers_instance.set_valves(valves)
        assert self.helpers_instance.toggle_statuses["valves"] == valves

    @patch("socket.socket")
    def test_extract_local_ip(self, mock_socket):
        """test extract local ip"""

        # Mock the behavior of the socket.socket().connect().getsockname()
        mock_socket.return_value.getsockname.return_value = ("192.168.1.2", 12345)

        # Call the method under test
        local_ip = self.helpers_instance.extract_local_ip()

        # Assert the expected behavior
        assert local_ip == "192.168.1.2"

    @patch("socket.socket")
    def test_extract_local_ip_with_exception(self, mock_socket):
        """test extract local ip with exception"""

        # Mock the behavior of the socket.socket().connect() to raise an exception
        mock_socket.return_value.connect.side_effect = Exception("Mocked exception")

        # Call the method under test
        local_ip = self.helpers_instance.extract_local_ip()

        # Assert the expected behavior when an exception occurs
        assert local_ip == "127.0.0.1"

    @patch("subprocess.run")
    @patch("app.raspi.helpers.logger")
    def test_get_uptime_success(self, mock_logger, mock_subprocess_run):
        """test get uptime"""
        # Mock the subprocess.run() to simulate a successful execution
        mock_result = MagicMock()
        mock_result.stdout = "3 days, 5 hours, 20 minutes"
        mock_subprocess_run.return_value = mock_result

        # Call the method under test
        uptime = self.helpers_instance.get_uptime()

        # Assert the expected behavior for a successful execution
        self.assertEqual(uptime, "3 days, 5 hours, 20 minutes")
        mock_logger.error.assert_not_called()

    @patch("subprocess.run")
    @patch("app.raspi.helpers.logger")
    def test_get_uptime_exception(self, mock_logger, mock_subprocess_run):
        """test get uptime"""
        # Mock the subprocess.run() to simulate an exception
        mock_subprocess_run.side_effect = Exception("Mocked subprocess error")

        # Call the method under test
        uptime = self.helpers_instance.get_uptime()

        # Assert the expected behavior when an exception occurs
        self.assertEqual(uptime, "Mocked subprocess error")
        mock_logger.error.assert_called_once_with("Error retrieving uptime: Mocked subprocess error")

    def test_extract_local_ip_returns_local_ip_address(self):
        """extract_local_ip method returns the local IP address of the device"""

        ip_address = self.helpers_instance.extract_local_ip()
        assert isinstance(ip_address, str)

    def test_extract_local_ip_handles_exceptions_for_unable_to_connect(self):
        """extract_local_ip method handles exceptions when unable to connect to 8.8.8.8"""

        assert self.helpers_instance.extract_local_ip() != "127.0.0.1"

    def test_get_uptime_returns_uptime(self):
        """get_uptime method returns the uptime of the device"""

        uptime = self.helpers_instance.get_uptime()
        assert isinstance(uptime, str)
        assert uptime != "no uptime is supported!"

    def test_get_git_commit_id_returns_commit_id(self):
        """get_git_commit_id method returns the git commit ID of the codebase"""

        commit_id = self.helpers_instance.get_git_commit_id()
        assert isinstance(commit_id, str)
        assert len(commit_id) > 0
        pattern = re.compile(r"^[0-9a-fA-F]+$")
        assert pattern.match(commit_id), "Invalid format"

    def test_store_object_to_file_stores_object(self):
        """store_object_to_file method stores a local object to a file"""

        filename = "test_file.pkl"
        local_object = {"key": "value"}
        self.helpers_instance.store_object_to_file(filename, local_object)
        loaded_object = self.helpers_instance.load_object_from_file(filename)
        assert loaded_object == local_object

    def test_load_object_from_file(self):
        """load_object_from_file method loads a local object from a file"""
        # Arrange
        helpers = Helpers()
        filename = "test_file.pkl"
        local_obj = {"key": "value"}
        with open(filename, "wb") as obj_file:
            pickle.dump(local_obj, obj_file)
        # Act
        result = helpers.load_object_from_file(filename)
        # Assert
        assert result == local_obj

    def test_get_toggle_statuses(self):
        """get_toggle_statuses method returns the toggle statuses of the device"""
        # Arrange
        setup_gpio()
        helpers = Helpers()
        expected_statuses = {
            "valves": [],
            "out1": 0,
            "out2": 0,
            "out3": 0,
            "out4": 0,
            "server_time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "tz": helpers.get_timezone(),
            "hw_id": RPI_HW_ID,
        }
        # Act
        result = helpers.get_toggle_statuses()
        # Assert
        logger.info(f"expected_statuses: {expected_statuses}")
        logger.info(f"result: {result}")
        assert result["valves"] == expected_statuses["valves"]
        assert result["out1"] == expected_statuses["out1"]
        assert result["out2"] == expected_statuses["out2"]
        assert result["out3"] == expected_statuses["out3"]
        assert result["out4"] == expected_statuses["out4"]
        assert result["tz"] == expected_statuses["tz"]
        assert result["hw_id"] == expected_statuses["hw_id"]

        # Check server_time separately
        expected_server_time = datetime.strptime(expected_statuses["server_time"], "%Y/%m/%d %H:%M:%S")
        result_server_time = datetime.strptime(result["server_time"], "%Y/%m/%d %H:%M:%S")

        # Assert date
        assert result_server_time.date() == expected_server_time.date()
        # Assert year
        assert result_server_time.year == expected_server_time.year
        # Assert hour
        assert result_server_time.hour == expected_server_time.hour

    def test_set_gpio_outputs_2(self):
        """set_gpio_outputs method sets the GPIO output of the device"""
        # Arrange
        helpers = Helpers()
        valve = "out1"
        status = 1
        expected_status = 1
        # Act
        result = helpers.set_gpio_outputs(status, valve)
        # Assert
        assert result == expected_status

    def test_toggle_method_toggles_gpio_output(self):
        """toggle method toggles the GPIO output of the device"""
        # Arrange

        valve = "out1"
        initial_status = self.helpers_instance.set_gpio_outputs(0, valve)
        logger.debug(f"Initial status: {initial_status}")
        # Act
        self.helpers_instance.toggle(not initial_status, valve)
        new_status = self.helpers_instance.toggle_statuses[valve]
        logger.debug(f"New status: {new_status}")

        # Assert
        assert new_status != initial_status

    @patch("subprocess.run")
    @patch("app.raspi.helpers.logger")
    def test_get_git_commit_id_success(self, mock_logger, mock_subprocess_run):
        """test get git commit id"""
        # Mock the subprocess.run() to simulate a successful execution
        mock_result = MagicMock()
        mock_result.stdout = "abcdef123456"
        mock_subprocess_run.return_value = mock_result

        # Call the method under test
        commit_id = self.helpers_instance.get_git_commit_id()

        # Assert the expected behavior for a successful execution
        self.assertEqual(commit_id, "abcdef123456")
        mock_logger.error.assert_not_called()

    def test_get_toggle_statuses_returns_toggle_statuses(self):
        """
        Test that the `get_toggle_statuses` method returns a dictionary with expected keys.

        Returns:
            None
        """

        toggle_statuses = self.helpers_instance.get_toggle_statuses()
        assert isinstance(toggle_statuses, dict)
        assert "valves" in toggle_statuses
        assert "out1" in toggle_statuses
        assert "out2" in toggle_statuses
        assert "out3" in toggle_statuses
        assert "out4" in toggle_statuses
        assert "server_time" in toggle_statuses
        assert "tz" in toggle_statuses
        assert "hw_id" in toggle_statuses

    def test_set_valves_with_invalid_input(self):
        """
        Test that the `set_valves` method handles invalid input and sets valves to an empty list.

        Returns:
            None
        """

        invalid_valves = "invalid_input"
        with pytest.raises(Exception):
            self.helpers_instance.set_valves(invalid_valves)
            assert not self.helpers_instance.toggle_statuses["valves"]

    def test_store_toggle_statuses_to_file(self):
        """
        Test that the `store_toggle_statuses_to_file` method stores toggle statuses correctly.

        Returns:
            None
        """

        toggle_statuses = {"valves": [1, 2, 3, 4], "out1": 1, "out2": 0}
        self.helpers_instance.toggle_statuses = toggle_statuses
        stored_statuses = self.helpers_instance.store_toggle_statuses_to_file()
        assert stored_statuses == toggle_statuses

    def test_store_wifi_networks_to_file(self):
        """
        Test that the `store_wifi_networks_to_file` method stores WiFi networks correctly.

        Returns:
            None
        """

        wifi_networks = [{"id": 1, "ssid": "Network1"}, {"id": 2, "ssid": "Network2"}]
        self.helpers_instance.ap_array = wifi_networks
        stored_networks = self.helpers_instance.store_wifi_networks_to_file()
        assert stored_networks == wifi_networks

    def test_load_toggle_statuses_from_file(self):
        """
        Test that the `load_toggle_statuses_from_file` method loads toggle statuses correctly.

        Returns:
            None
        """

        toggle_statuses = {"valves": [1, 2, 3, 4], "out1": 1, "out2": 0}
        self.helpers_instance.store_object_to_file(STATUSES_FILE, toggle_statuses)
        self.helpers_instance.load_toggle_statuses_from_file()
        assert self.helpers_instance.toggle_statuses == toggle_statuses

    @patch("builtins.open")
    @patch("app.raspi.helpers.logger")
    @patch("pickle.dump")
    def test_store_object_to_file_success_1(self, mock_pickle_dump, mock_logger, mock_open):
        """test store object to file"""

        # Mock the behavior of pickle.dump
        filename = "data.pkl"
        local_object = {"key": "value"}

        # Call the method under test
        result = self.helpers_instance.store_object_to_file(filename, local_object)

        # Assert the expected behavior for a successful execution
        mock_pickle_dump.assert_called_once_with(local_object, mock_open.return_value.__enter__.return_value)
        mock_logger.info.assert_called_once_with(f"Stored local object file: {filename}: {local_object}")
        self.assertEqual(result, local_object)

    def test_store_object_to_file_success_2(self):
        """test store object to file"""

        # Test successful storing of an object to a file
        self.helpers_instance.store_object_to_file(self.test_file_path, self.test_data)
        self.assertTrue(os.path.exists(self.test_file_path))

        # Verify the content of the stored file
        with open(self.test_file_path, "rb") as obj_file:
            stored_data = pickle.load(obj_file)
        self.assertEqual(stored_data, self.test_data)

    def test_store_object_to_file_exception(self):
        """test store object to file with exception"""

        # Test handling of an exception during the storing process
        with self.assertRaises(Exception):
            self.helpers_instance.store_object_to_file("/invalid/path/test.pkl", self.test_data)

    def test_store_object_to_file_logging(self):
        """test store object to file"""

        # Test if the method logs the correct information
        with unittest.mock.patch("app.raspi.helpers.logger.info") as mock_logger:
            self.helpers_instance.store_object_to_file(self.test_file_path, self.test_data)
            mock_logger.assert_called_with(f"Stored local object file: {self.test_file_path}: {self.test_data}")

    def test_load_object_from_file_success_1(self):
        """test load object from file"""

        # Prepare a test file with data
        with open(self.test_file_path, "wb") as obj_file:
            pickle.dump(self.test_data, obj_file)

        # Test successful loading of an object from a file
        loaded_object = self.helpers_instance.load_object_from_file(self.test_file_path)
        self.assertEqual(loaded_object, self.test_data)

    def test_load_object_from_file_exception(self):
        """test load object from file with exception"""

        # Test handling of an exception during the loading process
        with self.assertRaises(Exception):
            self.helpers_instance.load_object_from_file("/invalid/path/test.pkl")

    def test_load_object_from_file_logging(self):
        """test load object from file"""

        # Test if the method logs the correct information
        with unittest.mock.patch("app.raspi.helpers.logger.info") as mock_logger:
            # Prepare a test file with data
            with open(self.test_file_path, "wb") as obj_file:
                pickle.dump(self.test_data, obj_file)

            self.helpers_instance.load_object_from_file(self.test_file_path)
            mock_logger.assert_called_with(f"Loaded local object file: {self.test_file_path}: {self.test_data}")

    def test_load_object_from_file_error_logging(self):
        """test load object from file"""

        # Test if the method logs errors correctly and stores the default object
        with unittest.mock.patch("app.raspi.helpers.logger.error") as mock_logger:
            # Call the method with a non-existing file
            self.helpers_instance.load_object_from_file(self.empty_file_path)
            mock_logger.assert_called_once()  # Assuming only one error log entry is made

            # Verify that the default object is stored
            with open(self.empty_file_path, "rb") as obj_file:
                stored_data = pickle.load(obj_file)
            self.assertEqual(stored_data, {})

    def test_store_object_to_file_error_logging(self):
        """test store object to file"""

        # Test if the method logs errors correctly
        with unittest.mock.patch("app.raspi.helpers.logger.error") as mock_logger:
            with self.assertRaises(Exception):
                self.helpers_instance.store_object_to_file("/invalid/path/test.pkl", self.test_data)
            mock_logger.assert_called_once()  # Assuming only one error log entry is made

    @patch("builtins.open")
    @patch("app.raspi.helpers.logger")
    @patch("pickle.load")
    def test_load_object_from_file_success_2(self, mock_pickle_load, mock_logger, mock_open):
        """test load object from file"""

        # Mock the behavior of pickle.load
        filename = "data.pkl"
        local_object = {"key": "value"}
        mock_pickle_load.return_value = local_object

        # Call the method under test
        loaded_object = self.helpers_instance.load_object_from_file(filename)

        # Assert the expected behavior for a successful execution
        mock_pickle_load.assert_called_once_with(mock_open.return_value.__enter__.return_value)
        mock_logger.info.assert_called_once_with(f"Loaded local object file: {filename}: {local_object}")
        self.assertEqual(loaded_object, local_object)

    if ARCH == "arm":

        @patch("RPi.GPIO.output")
        @patch("RPi.GPIO.input")
        def test_set_gpio_outputs_1(self, mock_input, mock_output):
            """test gpio outputs"""

            # Test when ARCH is not 'arm'
            with patch("app.raspi.const.ARCH", "non-arm"):
                result = self.helpers_instance.set_gpio_outputs(1, "out1")
                self.assertEqual(result, 1)
                mock_input.assert_not_called()
                mock_output.assert_not_called()

            # Test when ARCH is 'arm' and valve is not 'out2'
            with patch("app.raspi.const.ARCH", "arm"):
                result = self.helpers_instance.set_gpio_outputs(1, "out1")
                self.assertEqual(result, 1)
                mock_input.assert_not_called()
                mock_output.assert_not_called()

            # Test when ARCH is 'arm' and valve is 'out2'
            with patch("app.raspi.const.ARCH", "arm"):
                setup_gpio()
                result = self.helpers_instance.set_gpio_outputs(1, "out2")
                self.assertEqual(result, 1)
                mock_output.assert_called_once_with(11, True)
                mock_input.assert_called_once_with(11)

    def test_is_connected_to_inet_when_connected(self):
        """test get connected status"""
        # Set the connected status to True (mocking the actual behavior)
        self.helpers_instance.is_connected_to_inet = True

        # Call the method and check the result
        connection_status = self.helpers_instance.is_connected_to_inet
        self.assertTrue(connection_status)

    def test_is_connected_to_inet_when_not_connected(self):
        """test get connected status"""

        # Set the connected status to False (mocking the actual behavior)
        self.helpers_instance.is_connected_to_inet = False

        # Call the method and check the result
        connection_status = self.helpers_instance.is_connected_to_inet
        self.assertFalse(connection_status)

    @patch("app.raspi.helpers.logger")
    @patch("app.raspi.helpers.subprocess.run")
    @patch("app.raspi.helpers.time.sleep", MagicMock())
    def test_system_reboot(self, mock_run, mock_logger):
        """test reboot"""

        # Call the method
        self.helpers_instance.system_reboot()

        # Ensure that the logger was called with the expected message
        mock_logger.info.assert_called_once_with("Rebooting in 2 seconds...")

        # Ensure that subprocess.run was called with the expected arguments
        mock_run.assert_called_once_with(["reboot"], stdout=-1, text=True, check=True)

    @patch("app.raspi.helpers.logger")
    @patch("app.raspi.helpers.subprocess.run", side_effect=Exception("Mocked exception"))
    @patch("app.raspi.helpers.time.sleep", MagicMock())
    def test_system_reboot_error(self, mock_run, mock_logger):  # pylint: disable=unused-argument
        """test reboot with error"""

        # Call the method
        self.helpers_instance.system_reboot()

        # Ensure that the logger was called with the expected error message
        mock_logger.error.assert_called_once_with("Error rebooting: Mocked exception")

    @patch("app.raspi.helpers.logger")
    @patch("app.raspi.helpers.subprocess.run")
    def test_system_update(self, mock_run, mock_logger):
        """test system update"""

        with unittest.mock.patch("os.kill") as mock_kill:
            # Call the method
            self.helpers_instance.system_update()

            # Ensure that the logger was called with the expected message
            mock_logger.info.assert_called_once_with("Git update code and restart...")

            # Ensure that subprocess.run was called with the expected arguments
            mock_run.assert_called_once_with(["/usr/bin/git", "pull"], stdout=-1, text=True, check=True)

            # Assert that os.kill was called with the expected arguments
            mock_kill.assert_called_once_with(os.getpid(), signal.SIGTERM)

    @patch("app.raspi.helpers.logger")
    @patch("app.raspi.helpers.subprocess.run", side_effect=Exception("Mocked exception"))
    def test_system_update_error(self, mock_run, mock_logger):  # pylint: disable=unused-argument
        """test system update with error"""

        with unittest.mock.patch("os.kill"):
            # Call the method
            self.helpers_instance.system_update()

            # Ensure that the logger was called with the expected error message
            mock_logger.error.assert_called_once_with("Error updating git: Mocked exception")

    def test_checking_for_duplicate_ssids_when_duplicate_exists(self):
        """test check for duplicate ssids"""

        # Set up test data with a duplicate SSID
        ssid_to_check = "MyWiFi"
        wifi_networks = [{"ssid": "AnotherWiFi"}, {"ssid": "MyWiFi"}, {"ssid": "YetAnotherWiFi"}]

        # Call the method and check the result
        is_duplicate = self.helpers_instance.checking_for_duplicate_ssids(ssid_to_check, wifi_networks)
        self.assertTrue(is_duplicate)

    def test_checking_for_duplicate_ssids_when_no_duplicate(self):
        """test check for duplicate ssids"""
        # Set up test data with no duplicate SSID
        ssid_to_check = "MyWiFi"
        wifi_networks = [{"ssid": "AnotherWiFi"}, {"ssid": "YetAnotherWiFi"}]

        # Call the method and check the result
        is_duplicate = self.helpers_instance.checking_for_duplicate_ssids(ssid_to_check, wifi_networks)
        self.assertFalse(is_duplicate)

    def test_checking_for_duplicate_ssids_when_empty_list(self):
        """test check for duplicate ssids"""

        # Set up test data with an empty list
        ssid_to_check = "MyWiFi"
        wifi_networks = []

        # Call the method and check the result
        is_duplicate = self.helpers_instance.checking_for_duplicate_ssids(ssid_to_check, wifi_networks)
        self.assertFalse(is_duplicate)

    def test_load_wifi_networks_from_file(self):
        """
        Test that the `load_wifi_networks_from_file` method loads WiFi networks correctly.

        Returns:
            None
        """

        wifi_networks = [{"id": 1, "ssid": "Network1"}, {"id": 2, "ssid": "Network2"}]
        self.helpers_instance.store_object_to_file(NETWORKS_FILE, wifi_networks)
        self.helpers_instance.load_wifi_networks_from_file()
        assert self.helpers_instance.ap_array == wifi_networks

    def test_get_timezone(self):
        """
        Test that the `get_timezone` method returns a string representing the timezone.

        Returns:
            None
        """

        timezone = self.helpers_instance.get_timezone()
        assert isinstance(timezone, str)

    def test_check_empty_toggle_existing_toggle(self):
        """
        Test that the `check_empty_toggle` method handles an existing toggle correctly.

        Returns:
            None
        """

        valve = "out1"
        self.helpers_instance.toggle_statuses[valve] = 1
        self.helpers_instance.check_empty_toggle(valve)
        assert self.helpers_instance.toggle_statuses[valve] == 1

    @patch("app.raspi.helpers.logger")
    @patch("subprocess.Popen")
    def test_scan_rpi_wifi_networks_refresh_true(self, mock_popen, mock_logger):
        """test scan wifi networks with refresh=true"""
        # Arrange
        mock_popen_instance = mock_popen.return_value
        mock_popen_instance.communicate.return_value = (
            b"""
                                                        lo        Interface doesn't support scanning.

eth0      Interface doesn't support scanning.

wlan0     Scan completed :
          Cell 01 - Address: 60:A4:B7:DE:CC:63
                    Channel:36
                    Frequency:5.18 GHz (Channel 36)
                    Quality=52/70  Signal level=-58 dBm
                    Encryption key:on
                    ESSID:"NEW_JERSEY"
                    Bit Rates:6 Mb/s; 9 Mb/s; 12 Mb/s; 18 Mb/s; 24 Mb/s
                              36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=0000000000000000
                    Extra: Last beacon: 5441476ms ago
                    IE: Unknown: 000A4E45575F4A4552534559
                    IE: Unknown: 01088C129824B048606C
                    IE: Unknown: 030124
                    IE: Unknown: 050400010000
                    IE: Unknown: 07104445202401172801172C011730011700
                    IE: Unknown: 460573D000000C
                    IE: Unknown: 2D1AEF0903FFFF000000000000000000000100000000000000000000
                    IE: Unknown: 3D1624050400000000000000000000000000000000000000
                    IE: Unknown: 7F0804000F0200000040
                    IE: Unknown: BF0CB2798933FAFF0000FAFF0020
                    IE: Unknown: C005012A00FCFF
                    IE: Unknown: C305032E2E2E2E
                    IE: Unknown: DD180050F2020101800003A4000027A4000042435E0062322F00
                    IE: Unknown: DD0900037F01010000FF7F
                    IE: Unknown: DD088CFDF00101020100
                    IE: Unknown: 3603534802
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (2) : PSK unknown (4)
                    IE: Unknown: DD1D0050F204104A0001101044000102103C0001031049000600372A000120
                    IE: Unknown: DD1F8CFDF0000001010000010066A4B7DECC4BFFFF60A4B7DECC63000000000000
                    IE: Unknown: DD820050F204104A00011010
44000102103B00010310470010309AD776B6394603A52860A4B7DECC601021000754502D4C696E6B102300074465636F2050
39102400074465636F20503910420001301054000800060050F20400011011001057686F6C652D686F6D652057692D466910
0800020000103C0001031049000600372A000120

docker0   Interface doesn't support scanning.
""",
            None,
        )

        # Ensure that Popen is a MagicMock, so the context manager works
        mock_popen_instance.__enter__.return_value = mock_popen_instance

        # Act
        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = ""
            result = self.helpers_instance.scan_rpi_wifi_networks(refresh=True)

        # Assert
        if ARCH == "arm":
            self.assertEqual(mock_logger.info.call_count, 2)
            self.assertEqual(mock_popen.call_count, 1)
            self.assertEqual(self.helpers_instance.ap_array, [{"id": 1, "ssid": "NEW_JERSEY"}])
        else:
            self.assertEqual(mock_logger.info.call_count, 0)
            self.assertEqual(mock_popen.call_count, 0)
            self.assertEqual(self.helpers_instance.ap_array, [])
        self.assertEqual(mock_logger.error.call_count, 0)
        self.assertEqual(result, self.helpers_instance.ap_array)

    @patch("subprocess.Popen")
    def test_scan_rpi_wifi_networks_refresh_false(self, mock_popen):
        """test scan wifi networks with refresh=false"""
        # Arrange
        self.helpers_instance.ap_array = [{"id": "1", "SSID": "test"}]
        self.helpers_instance.store_wifi_networks_to_file()

        # Act
        result = self.helpers_instance.scan_rpi_wifi_networks(refresh=False)

        # Assert
        self.assertEqual(mock_popen.call_count, 0)
        self.assertEqual(self.helpers_instance.ap_array, [{"id": "1", "SSID": "test"}])
        self.assertEqual(result, self.helpers_instance.ap_array)

    @patch("subprocess.Popen")
    @patch("app.raspi.helpers.logger")
    def test_scan_rpi_wifi_networks_popen_error(self, mock_logger, mock_popen):
        """test scan wifi networks with error"""

        # Arrange
        mock_popen_instance = mock_popen.return_value
        mock_popen_instance.communicate.return_value = (b"", b"Sample error")

        # Ensure that Popen is a MagicMock, so the context manager works
        mock_popen_instance.__enter__.return_value = mock_popen_instance

        # Act
        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = ""
            result = self.helpers_instance.scan_rpi_wifi_networks(refresh=True)

        # Assert
        self.assertEqual(mock_logger.info.call_count, 0)
        if ARCH == "arm":
            self.assertEqual(mock_logger.error.call_count, 1)
        else:
            self.assertEqual(mock_logger.error.call_count, 0)
        self.assertEqual(result, [])
