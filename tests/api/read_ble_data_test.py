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

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from raspirri.main_app import app
from raspirri.main_app import read_ble_data

client = TestClient(app)


class TestReadBleData:
    """
    Test class for the 'read_ble_data' function.
    """

    @pytest.mark.asyncio
    async def test_return_no_wifi_networks_identified(self):
        """
        Test for returning "No wifi networks identified!" when no wifi networks are found.
        """
        # Arrange

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await read_ble_data()

        # Assert
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "'>' not supported between instances of 'NoneType' and 'int'"

    @pytest.mark.asyncio
    async def test_raise_http_exception_invalid_arguments(self):
        """
        Test for raising an HTTPException with status code 500 and detail "Invalid request" when called with invalid arguments.
        """
        # Arrange
        invalid_arguments = "invalid"

        # Act and Assert
        with pytest.raises(HTTPException) as exc_info:
            await read_ble_data(invalid_arguments)
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "'>' not supported between instances of 'str' and 'int'"

    @pytest.mark.asyncio
    async def test_read_ble_data_success(self, mocker):
        """
        Test read BLE data with success.
        """
        # Arrange
        expected_response = {"wifi_networks": ["network1", "network2"]}  # Example response
        mocker.patch("raspirri.server.services.Services.discover_wifi_networks", return_value=expected_response)

        # Act
        response = client.get("/api/read_ble_data")

        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response

    @pytest.mark.asyncio
    async def test_read_ble_data_exception(self, mocker):
        """
        Test read BLE data with exception.
        """
        # Arrange
        mocker.patch("raspirri.server.services.Services.discover_wifi_networks", side_effect=Exception("Something went wrong"))

        # Act
        response = client.get("/api/read_ble_data")

        # Assert
        assert response.status_code == 500
        assert "Something went wrong" in response.text
