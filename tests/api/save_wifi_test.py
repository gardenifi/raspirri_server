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
from fastapi import HTTPException
from raspirri.main_app import WifiData, save_wifi
from raspirri.server.services import Services
from raspirri.server.const import DUMMY_SSID, DUMMY_PASSKEY, ARCH

services = Services()


class TestSaveWifi:
    """
    Test class for the 'save_wifi' function.
    """

    @pytest.mark.asyncio
    async def test_save_valid_wifi_data(self):
        """
        Test for saving valid wifi data.
        """
        data = WifiData(ssid=DUMMY_SSID, wifi_key=DUMMY_PASSKEY)
        if ARCH == "arm":
            response = await save_wifi(data)
            assert json.loads(response.body) == "OK"
        else:
            with pytest.raises(
                HTTPException,
            ):
                await save_wifi(data)

    @pytest.mark.asyncio
    async def test_return_200_status_code(self):
        """
        Test for returning a 200 status code for valid wifi data.
        """
        data = WifiData(ssid=DUMMY_SSID, wifi_key=DUMMY_PASSKEY)
        if ARCH == "arm":
            response = await save_wifi(data)
            assert response.status_code == 200
        else:
            with pytest.raises(
                HTTPException,
            ):
                await save_wifi(data)

    @pytest.mark.asyncio
    async def test_raise_http_exception_invalid_request(self):
        """
        Test for raising an HTTPException for invalid request.
        """
        with pytest.raises(PydanticValidationError):
            WifiData(ssid=None, wifi_key=None)

    @pytest.mark.asyncio
    async def test_save_wifi_data_empty_ssid(self):
        """
        Test for saving wifi data with an empty ssid.
        """
        data = WifiData(ssid="", wifi_key=DUMMY_PASSKEY)
        if ARCH == "arm":
            with pytest.raises(HTTPException) as exc_info:
                await save_wifi(data)
            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == ""
        else:
            with pytest.raises(
                HTTPException,
            ):
                await save_wifi(data)

    @pytest.mark.asyncio
    async def test_save_wifi_data_empty_wifi_key(self):
        """
        Test for saving wifi data with an empty wifi_key.
        """
        data = WifiData(ssid=DUMMY_SSID, wifi_key="")
        with pytest.raises(HTTPException) as exc_info:
            await save_wifi(data)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == ""

    @pytest.mark.asyncio
    async def test_save_wifi_data_empty_ssid_and_wifi_key(self):
        """
        Test for saving wifi data with an empty ssid and wifi_key.
        """
        data = WifiData(ssid="", wifi_key="")
        with pytest.raises(HTTPException) as exc_info:
            await save_wifi(data)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == ""
