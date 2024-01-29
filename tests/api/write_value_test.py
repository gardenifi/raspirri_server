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

import json
import pytest
from pydantic import ValidationError as PydanticValidationError
from fastapi import HTTPException, status
from app.main_app import write_ble_data, BleData, WifiData


class TestWriteBleData:
    """
    Test class for the 'write_ble_data' API endpoint.
    """

    @pytest.mark.asyncio
    async def test_valid_page_data(self):
        """
        API call with valid page data sets PAGE_SET and returns {"message": PAGE_SET}
        """
        # Arrange
        data = BleData(page=9)

        # Act
        response = await write_ble_data(data)

        # Assert
        assert json.loads(response.body) == {"page": 9}

    @pytest.mark.asyncio
    async def test_valid_refresh_data(self):
        """
        API call with valid refresh data sets REFRESH_SET and returns {"message": REFRESH_SET}
        """
        # Arrange
        data = BleData(refresh=True)

        # Act
        response = await write_ble_data(data)

        # Assert
        assert json.loads(response.body) == {"refresh": True}

    @pytest.mark.asyncio
    async def test_valid_ssid_and_wifi_key_data(self):
        """
        API call with valid ssid and wifi_key data stores ssid and wifi_key and returns {"message": connected}
        """
        # Arrange
        wifi_data = WifiData(ssid="test_ssid", wifi_key="test_key")
        data = BleData(wifi_data=wifi_data)

        # Act and Assert
        with pytest.raises(HTTPException) as exc:
            await write_ble_data(data)
        assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_invalid_page_data_type(self):
        """
        Invalid data type for refresh
        """
        # Act and Assert
        with pytest.raises(PydanticValidationError):
            BleData(page="invalid", refresh=0)

    @pytest.mark.asyncio
    async def test_invalid_refresh_data_type(self):
        """
        Invalid data type for refresh
        """
        # Arrange
        with pytest.raises(PydanticValidationError):
            BleData(refresh="invalid")

    @pytest.mark.asyncio
    async def test_invalid_ssid_data_type(self):
        """
        API call with invalid data type for ssid raises HTTPException with status_code 500
        """
        # Arrange
        data = BleData(ssid=123)

        # Act and Assert
        with pytest.raises(HTTPException) as exc:
            await write_ble_data(data)
        assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
