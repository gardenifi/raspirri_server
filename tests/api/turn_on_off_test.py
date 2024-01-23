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
from raspirri.main_app import ValveData, turn


class TestTurn:
    """
    Test class for the 'turn' function.
    """

    @pytest.mark.asyncio
    async def test_valid_input_turn_on_valve(self):
        """
        Test for turning on the specified valve with valid input.
        """
        # Arrange
        data = ValveData(status="1", valve="1")

        # Act
        response = await turn(data)

        # Assert
        assert response.status_code == 200
        assert json.loads(response.body) == {"message": "OK"}

    @pytest.mark.asyncio
    async def test_valid_input_turn_off_valve(self):
        """
        Test for turning off the specified valve with valid input.
        """
        # Arrange
        data = ValveData(status="0", valve="1")

        # Act
        response = await turn(data)

        # Assert
        assert response.status_code == 200
        assert json.loads(response.body) == {"message": "OK"}

    @pytest.mark.asyncio
    async def test_valid_input_return_status(self):
        """
        Test for returning the status of the valve with valid input.
        """
        # Arrange
        data = ValveData(status="1", valve="1")

        # Act
        response = await turn(data)

        # Assert
        assert response.status_code == 200
        assert json.loads(response.body) == {"message": "OK"}

    @pytest.mark.asyncio
    async def test_invalid_input_raises_http_exception(self):
        """
        Test for handling invalid input and raising an HTTPException with status code 422.
        """
        # Arrange
        data = ValveData(status="2", valve="1")

        # Act and Assert
        with pytest.raises(HTTPException) as exc:
            await turn(data)
        assert exc.value.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_fields_raises_http_exception(self):
        """
        Test for handling input with missing fields and raising an HTTPException with status code 500.
        """
        # Act and Assert
        data = ValveData(status="1")
        with pytest.raises(HTTPException) as exc:
            await turn(data)
        assert exc.value.status_code == 500
        assert exc.value.detail == ""

    @pytest.mark.asyncio
    async def test_invalid_data_types_raises_validation_exception(self):
        """
        Test for handling input with invalid data types and raising a Pydantic validation error.
        """
        # Act and Assert
        with pytest.raises(PydanticValidationError):
            ValveData(status=1, valve=1)
