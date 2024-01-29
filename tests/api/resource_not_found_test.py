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
from fastapi.testclient import TestClient
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.main_app import app
from app.main_app import resource_not_found

client = TestClient(app)
scope = {"type": "http", "http_version": "1.1", "method": "GET", "path": "/"}


@pytest.fixture(scope="function")
async def request_obj():
    """Request object creation fixture"""
    return Request(scope)


class TestResourceNotFound:
    """
    Test class for the 'resource_not_found' error handler function.
    """

    @pytest.mark.asyncio
    async def test_returns_json_response_with_status_code_404_and_detail_of_httpexception(self, obj=request_obj):
        """
        Test for returning a JSONResponse object with status code 404 and the detail of the HTTPException passed as an argument.
        """
        exc = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        response = await resource_not_found(obj, exc)
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert json.loads(response.body) == {"detail": "Not found"}

    @pytest.mark.asyncio
    async def test_handles_request_object_and_httpexception_object_as_arguments(self, obj=request_obj):
        """
        Test for handling a Request object and an HTTPException object as arguments.
        """
        exc = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        response = await resource_not_found(obj, exc)
        assert isinstance(response, JSONResponse)

    @pytest.mark.asyncio
    async def test_httpexception_detail_not_string(self, obj=request_obj):
        """
        Test for handling the case where the HTTPException passed as an argument has a detail attribute that is not a string.
        """
        exc = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=status.HTTP_404_NOT_FOUND)
        response = await resource_not_found(obj, exc)
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert json.loads(response.body) == {"detail": "404"}

    @pytest.mark.asyncio
    async def test_httpexception_no_detail_attribute(self, obj=request_obj):
        """
        Test for handling the case where the HTTPException passed as an argument has no detail attribute.
        """
        exc = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="")
        response = await resource_not_found(obj, exc)
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert json.loads(response.body) == {"detail": ""}

    @pytest.mark.asyncio
    async def test_request_object_is_none(self, obj=request_obj):
        """
        Test for handling the case where the Request object passed as an argument is None.
        """
        exc = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        response = await resource_not_found(obj, exc)
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert json.loads(response.body) == {"detail": "Not found"}
