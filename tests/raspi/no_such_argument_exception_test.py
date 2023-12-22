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

from app.raspi.exceptions import NoSuchArgumentException


class TestNoSuchArgumentException:
    """No Such Argument Exception Test Class"""

    def test_exception_message(self):
        """The exception is raised with the correct message when an argument is not found."""
        with pytest.raises(NoSuchArgumentException) as exc_info:
            raise NoSuchArgumentException("argument_name")
        assert str(exc_info.value) == "No such argument: argument_name"

    def test_argument_name(self):
        """The argument name is correctly stored in the exception instance."""
        try:
            raise NoSuchArgumentException("argument_name")
        except NoSuchArgumentException as e:
            assert e.argument_name == "argument_name"

    def test_exception_handling(self):
        """The exception can be caught and handled by the calling code."""
        try:
            raise NoSuchArgumentException("argument_name")
        except NoSuchArgumentException:
            assert True

    def test_empty_argument_name(self):
        """The argument name can be an empty string."""
        try:
            raise NoSuchArgumentException("")
        except NoSuchArgumentException as e:
            assert e.argument_name == ""

    def test_special_characters_argument_name(self):
        """The argument name can contain special characters."""
        try:
            raise NoSuchArgumentException("!@#$%^&*()")
        except NoSuchArgumentException as e:
            assert e.argument_name == "!@#$%^&*()"

    def test_number_argument_name(self):
        """The argument name can be a number."""
        try:
            raise NoSuchArgumentException("123")
        except NoSuchArgumentException as e:
            assert e.argument_name == "123"
