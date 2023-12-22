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
    from app.ble.exceptions import NotSupportedException

    NOT_SUPPORTED_PREFIX = "org.bluez.Error.NotSupported: "

    class TestNotSupportedException:
        """Not Supported Exception Test Class"""

        def test_dbus_error_name_attribute(self):
            """The _dbus_error_name attribute should be set to "org.bluez.Error.NotSupported" """
            error = NotSupportedException()
            assert error._dbus_error_name == "org.bluez.Error.NotSupported"  # pylint: disable=protected-access

        def test_empty_exception_message(self):
            """The exception message should be empty by default"""
            error = NotSupportedException()
            assert str(error) == NOT_SUPPORTED_PREFIX

        def test_custom_exception_message(self):
            """Passing a custom message to the constructor should set the exception message"""
            message = "This feature is not supported"
            error = NotSupportedException(message)
            assert str(error) == NOT_SUPPORTED_PREFIX + message

        def test_override_dbus_error_name(self):
            """The _dbus_error_name attribute should be overridable"""
            custom_error_name = "org.custom.Error.NotSupported"
            error = NotSupportedException()
            error._dbus_error_name = custom_error_name  # pylint: disable=protected-access
            assert error._dbus_error_name == custom_error_name  # pylint: disable=protected-access

        def test_non_string_exception_message(self):
            """The exception should be able to handle non-string messages"""
            message = 12345
            error = NotSupportedException(message)
            assert str(error) == NOT_SUPPORTED_PREFIX + str(message)
