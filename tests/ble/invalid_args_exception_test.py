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

from app.raspi.const import ARCH

if ARCH == "arm":
    import dbus

    from app.ble.exceptions import InvalidArgsException

    INVALID_ARGS_PREFIX = "org.freedesktop.DBus.Error.InvalidArgs: "

    class TestInvalidArgsException:
        """Invalid Args Exception Test Class"""

        def test_can_be_raised_with_no_arguments(self):
            """Can be raised with no arguments"""
            try:
                raise InvalidArgsException()
            except InvalidArgsException as e:
                assert str(e) == INVALID_ARGS_PREFIX

        def test_can_be_raised_with_a_message_argument(self):
            """Can be raised with a message argument"""
            try:
                raise InvalidArgsException("Invalid arguments")
            except InvalidArgsException as e:
                assert str(e) == INVALID_ARGS_PREFIX + "Invalid arguments"

        def test_can_be_caught_and_handled_by_try_except_block(self):
            """Can be caught and handled by a try-except block"""
            try:
                raise InvalidArgsException("Invalid arguments")
            except InvalidArgsException as e:
                assert str(e) == INVALID_ARGS_PREFIX + "Invalid arguments"

        def test_can_be_raised_with_a_non_string_argument(self):
            """Can be raised with a non-string argument"""
            try:
                raise InvalidArgsException(123)
            except InvalidArgsException as e:
                assert str(e) == INVALID_ARGS_PREFIX + "123"

        def test_can_be_raised_with_an_empty_string_argument(self):
            """Can be raised with an empty string argument"""
            try:
                raise InvalidArgsException("")
            except InvalidArgsException as e:
                assert str(e) == INVALID_ARGS_PREFIX

        def test_can_be_raised_with_a_string_containing_special_characters(self):
            """Can be raised with a string containing special characters"""
            try:
                raise InvalidArgsException("!@#$%^&*()")
            except InvalidArgsException as e:
                assert str(e) == INVALID_ARGS_PREFIX + "!@#$%^&*()"

        def test_inherits_from_dbus_exception(self):
            """Inherits from dbus.exceptions.DBusException"""
            assert issubclass(InvalidArgsException, dbus.exceptions.DBusException)

        def test_can_be_raised_and_caught_within_same_module(self):
            """Can be raised and caught within the same module"""
            try:
                raise InvalidArgsException()
            except InvalidArgsException:
                assert True

        def test_can_be_raised_with_non_ascii_string(self):
            """Can be raised with a string containing non-ASCII characters"""
            try:
                raise InvalidArgsException("非ASCII字符")
            except InvalidArgsException as e:
                assert str(e) == INVALID_ARGS_PREFIX + "非ASCII字符"
