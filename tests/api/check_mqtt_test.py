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

from fastapi import HTTPException, status
from app.main_app import check_mqtt


class TestCheckMqtt:
    """Check MQTT Test Class"""

    @pytest.mark.asyncio
    async def test_mqtt_thread_already_running(self, mocker):
        """
        Test case for checking the MQTT thread status when it is already running.

        Returns:
            None
        """
        mocker.patch("app.main_app.Mqtt.is_running", return_value=True)
        response = await check_mqtt()
        assert response.status_code == status.HTTP_200_OK
        assert json.loads(response.body) == {"detail": "MQTT thread was already running!"}

    @pytest.mark.asyncio
    async def test_start_mqtt_thread(self, mocker):
        """
        Test case for starting the MQTT thread when it is not already running.

        Returns:
            None
        """
        mocker.patch("app.main_app.Mqtt.is_running", return_value=False)
        response = await check_mqtt()
        assert response.status_code == status.HTTP_200_OK
        assert json.loads(response.body) == {"detail": "MQTT thread just started!"}

    @pytest.mark.asyncio
    async def test_exception_checking_mqtt_status(self, mocker):
        """
        Test case for handling an exception when checking the MQTT thread status.

        Returns:
            None
        """
        mocker.patch("app.main_app.Mqtt.is_running", side_effect=Exception)
        with pytest.raises(HTTPException) as exc_info:
            await check_mqtt()
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == ""

    @pytest.mark.asyncio
    async def test_exception_starting_mqtt_thread(self, mocker):
        """
        Test case for handling an exception when starting the MQTT thread.

        Returns:
            None
        """
        mocker.patch("app.main_app.Mqtt.is_running", return_value=False)
        mocker.patch("app.main_app.Mqtt.start_mqtt_thread", side_effect=Exception)
        with pytest.raises(HTTPException) as exc_info:
            await check_mqtt()
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == ""

    @pytest.mark.asyncio
    async def test_exception_checking_and_starting_mqtt_thread(self, mocker):
        """
        Test case for handling an exception when both checking and starting the MQTT thread.

        Returns:
            None
        """
        mocker.patch("app.main_app.Mqtt.is_running", return_value=False)
        mocker.patch("app.main_app.Mqtt.start_mqtt_thread", side_effect=Exception)
        with pytest.raises(HTTPException) as exc_info:
            await check_mqtt()
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == ""

    @pytest.mark.asyncio
    async def test_exception_starting_mqtt_thread_with_running_mqtt(self, mocker):
        """
        Test case for handling an exception when starting the MQTT thread with a running MQTT thread.

        Returns:
            None
        """
        mocker.patch("app.main_app.Mqtt.is_running", return_value=True)
        mocker.patch("app.main_app.Mqtt.start_mqtt_thread", side_effect=Exception)
        await check_mqtt()
