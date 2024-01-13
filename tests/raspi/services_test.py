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

import os
import subprocess
import json
import unittest
from unittest.mock import MagicMock
import pytest
from loguru import logger
from app.raspi.services import Services
from app.raspi.const import RPI_HW_ID, MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASS, PROGRAM, ARCH, MAX_NUM_OF_BYTES_CHUNK


if ARCH == "arm":
    split_json_into_chunks_params = [
        (10, 1, 1),
        (11, 2, 1),
        (12, 2, 2),
        (20, 3, 2),
        (100, 11, 5),
        (1000, 124, 1),
        (1000, 124, 123),
        (55, 6, 5),
        (56, 7, 6),
    ]
else:
    split_json_into_chunks_params = [
        (10, 1, 1),
        (11, 1, 1),
        (12, 2, 2),
        (20, 2, 2),
        (100, 11, 5),
        (1000, 124, 1),
        (1000, 124, 123),
        (55, 6, 5),
        (56, 6, 6),
    ]


@pytest.fixture(autouse=True)
def setup():
    """
    A pytest fixture that is automatically used before and after each test function.
    It is responsible for deleting all programs json files.
    """
    # delete all json files first
    # List all files in the directory
    files = os.listdir(".")

    # Filter JSON files
    json_files = [file for file in files if file.startswith(PROGRAM)]

    # Delete each test JSON file
    for json_file in json_files:
        file_path = os.path.join(".", json_file)
        os.remove(file_path)
        logger.info(f"Deleted: {file_path}")


class TestServices:
    """Service Test Class"""

    def test_delete_program(self):
        """can delete program"""
        services = Services()

        valve = 1

        result = services.delete_program(valve)

        assert result is False

        # Create a program file to delete
        program_data = {
            "days": "mon,tue,wed",
            "tz_offset": 2,
            "cycles": [
                {"start": "08:00", "min": "30"},
                {"start": "14:00", "min": "45"},
            ],
            "out": 1,
        }
        services.store_program_cycles(program_data, True)

        result = services.delete_program(valve)

        assert result is True

    def test_load_program_cycles_if_exists(self):
        """can load program cycles if exists"""
        services = Services()

        valve = 1

        result = services.load_program_cycles_if_exists(valve)

        assert result is None

        # Create a program file to load
        program_data = {
            "days": "mon,tue,wed",
            "tz_offset": 2,
            "cycles": [
                {"start": "08:00", "min": "30"},
                {"start": "14:00", "min": "45"},
            ],
            "out": 1,
        }
        services.store_program_cycles(program_data, True)

        result = services.load_program_cycles_if_exists(valve)

        assert result == program_data

    def test_invalid_cycle_in_store_program_cycles(self):
        """invalid cycle in store program cycles"""

        services = Services()

        program_data = {
            "days": "mon,tue,wed",
            "tz_offset": 2,
            "cycles": [
                {"start": "08:00", "min": "30"},
                {"start": "14:00", "min": "-45"},
            ],
            "out": 1,
        }

        services.store_program_cycles(program_data)

    @pytest.mark.parametrize(("wifi_ssids", "expected_pages", "selected_page"), split_json_into_chunks_params)
    def test_split_json_into_chunks(self, wifi_ssids: int, expected_pages: int, selected_page: int) -> None:
        """can split json into chunks"""
        services = Services()

        expected_result = {
            "hw_id": RPI_HW_ID,
            "mqtt_broker": {"host": MQTT_HOST, "port": int(MQTT_PORT), "user": MQTT_USER, "pass": MQTT_PASS},
            "page": selected_page,
            "nets": {"not checking"},
            "pages": expected_pages,
        }

        ap_array = [{"id": i, "ssid": f"test_wifi{i}"} for i in range(wifi_ssids)]
        actual_result = services.split_json_into_chunks(selected_page, ap_array)
        logger.info(f"Checking Results for Page: {selected_page}")
        logger.info(f"Actual   Result: {actual_result}")
        logger.info(f"Expected Result: {expected_result}")
        logger.info(f"Actual   Result[pages]: {actual_result['pages']}")
        logger.info(f"Expected Result[pages]: {expected_result['pages']}")

        assert actual_result["hw_id"] == expected_result["hw_id"]
        assert actual_result["mqtt_broker"] == expected_result["mqtt_broker"]
        assert actual_result["page"] == expected_result["page"]
        assert actual_result["pages"] == expected_result["pages"]

        if expected_pages == 1:
            expected_result["nets"] = ap_array
            assert actual_result["nets"] == expected_result["nets"]

        size_of_page = len(json.dumps(actual_result).encode("utf-8"))
        logger.info(f"Checking size of Page: {selected_page}: {size_of_page}")
        assert size_of_page < MAX_NUM_OF_BYTES_CHUNK

    def test_discover_wifi_networks(self):
        """can discover wifi networks"""

        services = Services()

        result = services.discover_wifi_networks()

        assert result is not None
        assert isinstance(result, str)

        result = services.discover_wifi_networks(page=2)

        assert result is not None
        assert isinstance(result, str)

    def test_save_wifi_network(self):
        """can save wifi network"""

        services = Services()
        if ARCH == "arm":
            with pytest.raises(
                subprocess.CalledProcessError,
                match="Command 'sudo nmcli device wifi " + "connect test_ssid password test_key' " + "returned non-zero exit status 10.",
            ):
                result = services.save_wifi_network("test_ssid", "test_key")
                assert result == "OK"
        else:
            with pytest.raises(
                TypeError,
                match=f"{ARCH} architecture is not supported!!!",
            ):
                result = services.save_wifi_network("test_ssid", "test_key")

    def test_save_wifi_network_with_wpa(self):
        """can save wifi network with wpa"""

        services = Services()

        if ARCH == "arm":
            with pytest.raises(
                subprocess.CalledProcessError,
                match="Command 'sudo nmcli device wifi connect 1 password " + "test_key' returned non-zero exit status 10.",
            ):
                result = services.save_wifi_network_with_wpa("1", "test_key")
                assert result == "OK"
        else:
            with pytest.raises(
                TypeError,
                match=f"{ARCH} architecture is not supported!!!",
            ):
                result = services.save_wifi_network("test_ssid", "test_key")

    def test_turn_on_from_program(self):
        """can turn on from program"""

        services = Services()

        services.turn_on_from_program(1)

        # Add assertions here

    def test_turn_off_from_program(self):
        """can turn off from program"""

        services = Services()

        services.turn_off_from_program(1)

        # Add assertions here

    def test_invalid_json_in_split_json_into_chunks(self):
        """invalid json in split json into chunks"""

        services = Services()

        page = 1
        ap_array = [{"ssi": "test_wifi1"}]

        response = services.split_json_into_chunks(page, ap_array)
        assert response["hw_id"] == RPI_HW_ID
        assert response["mqtt_broker"]["host"] == "localhost"
        assert response["mqtt_broker"]["port"] == 1883
        assert response["mqtt_broker"]["user"] == "user"
        assert response["mqtt_broker"]["pass"] == "pass"
        assert response["page"] == 1
        assert response["nets"][0]["ssi"] == "test_wifi1"
        assert response["pages"] == 1

    def test_invalid_request_in_save_wifi_network(self):
        """invalid request in save wifi network"""

        services = Services()

        if ARCH == "arm":
            with pytest.raises(Exception):
                services.save_wifi_network(None, None)
        else:
            with pytest.raises(TypeError, match=f"{ARCH} architecture is not supported!!!"):
                services.save_wifi_network(None, None)

    def test_invalid_request_in_save_wifi_network_with_wpa(self):
        """invalid request in save wifi network with wpa"""

        services = Services()
        if ARCH == "arm":
            with pytest.raises(Exception):
                services.save_wifi_network_with_wpa(None, None)
        else:
            with pytest.raises(TypeError, match=f"{ARCH} architecture is not supported!!!"):
                services.save_wifi_network_with_wpa(None, None)

    def test_can_get_stop_datetime(self):
        """can get stop datetime"""

        services = Services()
        day = "mon"
        start_hour = 8
        start_min = 0
        period = 30

        stop_day, stop_hour, stop_min = services.get_stop_datetime(day, start_hour, start_min, period)

        assert stop_day == "mon"
        assert stop_hour == 8
        assert stop_min == 30

    def test_get_stop_datetime(self):
        """Test get_stop_datetime"""
        # Create an instance of your class
        services = Services()

        # Test case 1
        result = services.get_stop_datetime("mon", 10, 30, 45)
        assert result == ("mon", 11, 15)

        # Test case 2
        result = services.get_stop_datetime("fri", 23, 45, 30)
        assert result == ("sat", 0, 15)

    def test_store_program_cycles(self):
        """Test program cycles"""
        services = Services()
        services.scheduler = MagicMock()
        services.scheduler_started = False

        # Test case 1: Valid data, store=False
        json_data = {
            "days": "mon,tue",
            "tz_offset": 2,
            "cycles": [{"min": 30, "start": "12:00"}, {"min": 45, "start": "15:30"}],
            "out": "output_device",
        }
        services.store_program_cycles(json_data, store=False)
        assert services.scheduler.add_job.call_count == 2

        # Test case 2: Valid data, store=True
        services.store_program_cycles(json_data, store=True)
        assert services.scheduler.add_job.call_count == 4

        # Test case 3: Exception handling
        json_data_exception = {
            "days": "mon1,tue",
            "cycles": [{"min": 30, "start": "12:00"}, {"min": 45, "start": "15:30"}],
            "out": "output_device",
        }

        # Mock the logger to capture log messages
        with unittest.mock.patch("app.raspi.services.logger.error") as mock_logger_error:
            # Raise an exception during the method call
            with pytest.raises(Exception):
                services.store_program_cycles(json_data_exception, store=False)

            # Verify that the exception is logged
            assert mock_logger_error.call_count == 1
