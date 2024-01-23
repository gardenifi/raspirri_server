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
    import pytest

    from raspirri.ble.service import Characteristic
    from raspirri.ble.service import CharacteristicUserDescriptionDescriptor
    from raspirri.ble.exceptions import NotPermittedException

    class TestCharacteristicUserDescriptionDescriptor:
        """Characteristic User Description Descriptor Test Class"""

        def test_read_value(self, setup_service):
            """can read the value of the descriptor"""
            characteristic = Characteristic(uuid="1234", flags=["read", "write"], service=setup_service)
            descriptor = CharacteristicUserDescriptionDescriptor(characteristic)
            assert descriptor.ReadValue(options={}) == descriptor.value

        def test_write_value(self, setup_service):
            """can write a new value to the descriptor if it is writable"""
            characteristic = Characteristic(uuid="1234", flags=["read", "write", "writable-auxiliaries"], service=setup_service)
            descriptor = CharacteristicUserDescriptionDescriptor(characteristic)
            new_value = [1, 2, 3]
            descriptor.WriteValue(values=new_value, options={})
            assert descriptor.value == new_value

        def test_default_value(self, setup_service):
            """initializes with a default value"""
            characteristic = Characteristic(uuid="1234", flags=["read", "write"], service=setup_service)
            descriptor = CharacteristicUserDescriptionDescriptor(characteristic)
            assert descriptor.value == [
                84,
                104,
                105,
                115,
                32,
                105,
                115,
                32,
                97,
                32,
                99,
                104,
                97,
                114,
                97,
                99,
                116,
                101,
                114,
                105,
                115,
                116,
                105,
                99,
                32,
                102,
                111,
                114,
                32,
                116,
                101,
                115,
                116,
                105,
                110,
                103,
            ]

        def test_write_read_only(self, setup_service):
            """raises NotPermittedException when attempting to write to a read-only descriptor"""
            characteristic = Characteristic(uuid="1234", flags=["read"], service=setup_service)
            descriptor = CharacteristicUserDescriptionDescriptor(characteristic)
            with pytest.raises(NotPermittedException):
                descriptor.WriteValue(values=[1, 2, 3], options={})

        def test_read_empty_value(self, setup_service):
            """returns an empty array when attempting to read from a descriptor with no value"""
            characteristic = Characteristic(uuid="1234", flags=["read", "write"], service=setup_service)
            descriptor = CharacteristicUserDescriptionDescriptor(characteristic)
            descriptor.value = []
            assert descriptor.ReadValue(options={}) == []

        def test_non_ascii_characters(self, setup_service):
            """can handle non-ascii characters in the descriptor value"""
            characteristic = Characteristic(uuid="1234", flags=["read", "write"], service=setup_service)
            descriptor = CharacteristicUserDescriptionDescriptor(characteristic)
            descriptor.value = [195, 169, 195, 170, 195, 171]
            assert descriptor.ReadValue(options={}) == [195, 169, 195, 170, 195, 171]

        def test_handle_large_values(self, setup_service):
            """can handle large values for the descriptor"""
            characteristic = Characteristic(uuid="1234", flags=["read", "write", "writable-auxiliaries"], service=setup_service)
            descriptor = CharacteristicUserDescriptionDescriptor(characteristic)
            large_value = [1] * 1000000
            descriptor.WriteValue(large_value, options={})
            assert descriptor.ReadValue(options={}) == large_value

        def test_handle_empty_values(self, setup_service):
            """can handle empty values for the descriptor"""
            characteristic = Characteristic(uuid="1234", flags=["read", "write", "writable-auxiliaries"], service=setup_service)
            descriptor = CharacteristicUserDescriptionDescriptor(characteristic)
            empty_value = []
            descriptor.WriteValue(empty_value, options={})
            assert descriptor.ReadValue(options={}) == empty_value

        def test_handle_multiple_requests(self, setup_service):
            """can handle multiple simultaneous read/write requests"""
            characteristic = Characteristic(uuid="1234", flags=["read", "write", "writable-auxiliaries"], service=setup_service)
            descriptor = CharacteristicUserDescriptionDescriptor(characteristic)
            value1 = [1, 2, 3]
            value2 = [4, 5, 6]
            descriptor.WriteValue(value1, options={})
            assert descriptor.ReadValue(options={}) == value1
            descriptor.WriteValue(value2, options={})
            assert descriptor.ReadValue(options={}) == value2
