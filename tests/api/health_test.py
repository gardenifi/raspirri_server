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

from fastapi import status
from fastapi.testclient import TestClient
from raspirri.main_app import app


client = TestClient(app)


class TestHealthCheck():
    """
    Test class for the Index API endpoints.
    """

    @pytest.mark.asyncio
    async def test_get_request_api_endpoint(self):
        """
        Test for GET request on "/api" endpoint, expecting a JSON response with a health message.
        """
        response = client.get("/api")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "RaspirriV1 Web Services API is Healthy!"}

    @pytest.mark.asyncio
    async def test_get_request_api_health_endpoint(self):
        """
        Test for GET request on "/api/health" endpoint, expecting a JSON response with a health message.
        """
        response = client.get("/api/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "RaspirriV1 Web Services API is Healthy!"}

    @pytest.mark.asyncio
    async def test_post_request_api_endpoint(self):
        """
        Test for POST request on "/api" endpoint, expecting an error response for Method Not Allowed.
        """
        response = client.post("/api")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response.json() == {"detail": "Method Not Allowed"}

    @pytest.mark.asyncio
    async def test_post_request_api_health_endpoint(self):
        """
        Test for POST request on "/api/health" endpoint, expecting an error response for Method Not Allowed.
        """
        response = client.post("/api/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response.json() == {"detail": "Method Not Allowed"}

    @pytest.mark.asyncio
    async def test_get_request_invalid_endpoint(self):
        """
        Test for GET request on an invalid endpoint, expecting an error response for Not Found.
        """
        response = client.get("/invalid")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Not Found"}

    @pytest.mark.asyncio
    async def test_put_request_invalid_endpoint(self):
        """
        Test for PUT request on an invalid endpoint, expecting an error response for Not Found.
        """
        response = client.put("/invalid")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Not Found"}

    @pytest.mark.asyncio
    def test_health_check_when_healthy(self, mocker):
        # Arrange
        mocker.patch("raspirri.main_app.Mqtt.is_healthy", return_value=True)

        # Act
        response = client.get("/api/health")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "RaspirriV1 Web Services API is Healthy!"}

    @pytest.mark.asyncio
    def test_health_check_when_not_healthy(self, mocker):
        # Arrange
        mocker.patch("raspirri.main_app.Mqtt.is_healthy", return_value=False)

        # Act
        response = client.get("/api/health")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"message": "RaspirriV1 Web Services API is NOT Healthy!"}
