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

import subprocess
import unittest
from unittest.mock import patch
import requests
from loguru import logger
from fastapi.testclient import TestClient
from raspirri.main_app import app
from raspirri.main_watchdog import check_process, check_health, restart_process, reboot_machine

client = TestClient(app)


class TestWatchdog(unittest.TestCase):

    """
    Test class for the Watchdog API client.
    """

    def setUp(self):
        # Create a list to capture log records
        self.log_records = []

        # Patch the logger to use a custom sink for testing
        def testing_sink(record):
            self.log_records.append(record)

        logger.add(testing_sink, level="INFO", catch=True)

    def tearDown(self):
        # Remove the testing sink from the logger
        logger.remove()

    @patch("subprocess.check_output")
    def test_check_process_running(self, mock_check_output):
        """
        Mock subprocess.check_output with success result.
        """
        # Arrange
        mock_check_output.return_value = b"active\n"

        # Act
        result = check_process("some_process")

        # Assert
        assert result is True
        mock_check_output.assert_called_once_with(["systemctl", "is-active", "some_process"])

    @patch("subprocess.check_output")
    def test_check_process_not_running(self, mock_check_output):
        """
        Mock subprocess.check_output with not-running result.
        """
        # Arrange
        mock_check_output.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["systemctl", "is-active", "some_process"])

        # Act
        result = check_process("some_process")

        # Assert
        assert result is False
        mock_check_output.assert_called_once_with(["systemctl", "is-active", "some_process"])

    @patch("requests.get")
    def test_check_health_success(self, mock_get):
        """
        Mock requests.get with success result.
        """
        # Arrange
        mock_get.return_value.status_code = requests.codes.ok

        # Act
        result = check_health("https://example.com/api/health")

        # Assert
        assert result is True

    @patch("requests.get")
    def test_check_health_failure(self, mock_get):
        """
        Mock requests.get with error result.
        """
        # Arrange
        mock_get.return_value.status_code = requests.codes.bad_request

        # Act
        result = check_health("https://example.com/api/health")

        # Assert
        assert result is False

    @patch("subprocess.run")
    def test_restart_process(self, mock_subprocess_run):
        """
        Mock subprocess.run with success result.
        """
        # Act
        restart_process("some_process")

        # Assert
        mock_subprocess_run.assert_called_once_with(["systemctl", "restart", "some_process"], check=True)

    @patch("subprocess.run")
    def test_reboot_machine(self, mock_subprocess_run):
        """
        Mock subprocess.run with success result.
        """
        # Act
        reboot_machine()

        # Assert
        mock_subprocess_run.assert_called_once_with(["sudo", "reboot"], check=True)

    @patch("requests.get")
    def test_exception_handling(self, mock_get):
        """
        Mock requests.get to check exception handler.
        """
        # Mocking a request exception
        mock_get.side_effect = Exception("Mocked Request Exception")

        # Endpoint to test
        endpoint = "http://example.com/api"

        # Calling the function and asserting the return value
        self.assertFalse(check_health(endpoint))

        # Asserting that the logger.error is called with the appropriate message
        self.assertTrue(any("Error HTTP request:"), self.log_records)
        self.assertTrue(any("Mocked Request Exceptiont"), self.log_records)
