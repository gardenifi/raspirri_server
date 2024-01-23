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
from raspirri.main_app import discover_wifi
from raspirri.server.services import Services

services = Services()


class TestDiscoverWifi:
    """
    Test class for the discover_wifi function.
    """

    @pytest.mark.asyncio
    async def test_no_parameters(self):
        """
        Test case for discover_wifi with no parameters.
        """
        response = await discover_wifi()
        assert response.status_code == 200
        assert json.loads(response.body) == services.discover_wifi_networks()

    @pytest.mark.asyncio
    async def test_chunked_0(self):
        """
        Test case for discover_wifi with chunked parameter set to 0.
        """
        response = await discover_wifi(chunked=0)
        assert response.status_code == 200
        assert json.loads(response.body) == services.discover_wifi_networks()

    @pytest.mark.asyncio
    async def test_chunked_1_page_1(self):
        """
        Test case for discover_wifi with chunked parameter set to 1 and page parameter set to 1.
        """
        response = await discover_wifi(chunked=1, page=1)
        assert response.status_code == 200
        assert json.loads(response.body) == services.discover_wifi_networks(chunked=1, page=1)
