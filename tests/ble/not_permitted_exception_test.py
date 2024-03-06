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

from raspirri.server.const import ARCH

if ARCH == "arm":
    import dbus

    from raspirri.ble.exceptions import NotPermittedException

    NOT_PERMITTED_EXCEPTION_PREFIX = "org.bluez.Error.NotPermitted: "

    class TestNotPermittedException:
        """Not Permitted Exception Test Class"""

        def test_can_be_raised_with_no_arguments(self):
            """Can be raised with no arguments"""
            try:
                raise NotPermittedException()
            except NotPermittedException:
                assert True
            else:
                assert False

        def test_can_be_raised_with_a_message_argument(self):
            """Can be raised with a message argument"""
            try:
                raise NotPermittedException("This action is not permitted")
            except NotPermittedException:
                assert True
            else:
                assert False

        def test_inherits_from_dbus_exceptions_dbusexception(self):
            """Inherits from dbus.exceptions.DBusException"""
            assert issubclass(NotPermittedException, dbus.exceptions.DBusException)

        def test_has_a_dbus_error_name_attribute(self):
            """Has a _dbus_error_name attribute"""
            assert hasattr(NotPermittedException, "_dbus_error_name")

        def test_can_be_caught_and_handled_by_try_except_blocks(self):
            """Can be caught and handled by try/except blocks"""
            try:
                raise NotPermittedException()
            except NotPermittedException:
                assert True
            else:
                assert False

        def test_can_be_subclassed(self):
            """Can be subclassed to create custom exceptions"""

            class CustomException(NotPermittedException):
                """Custom Exception Class"""

            try:
                raise CustomException()
            except CustomException:
                assert True

        def test_can_be_raised_with_custom_error_message(self):
            """Can be raised with a custom error message"""
            try:
                raise NotPermittedException("Custom error message")
            except NotPermittedException as e:
                assert str(e) == NOT_PERMITTED_EXCEPTION_PREFIX + "Custom error message"

        def test_can_be_raised_with_custom_error_name_and_message(self):
            """Can be raised with both a custom error name and message"""
            try:
                raise NotPermittedException("Custom error message")
            except NotPermittedException as e:
                assert str(e) == NOT_PERMITTED_EXCEPTION_PREFIX + "Custom error message"
                assert e._dbus_error_name == "org.bluez.Error.NotPermitted"  # pylint: disable=protected-access
