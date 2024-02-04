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

import os
import math
from raspirri.server.const import load_env_variable


class TestLoadEnvVariable:

    """Load Env Variable Test Class"""

    def test_returns_env_variable_value_if_exists(self):
        """Returns the value of the environment variable if it exists."""
        os.environ["VARNAME"] = "value"
        assert load_env_variable("VARNAME", "default") == "value"
        del os.environ["VARNAME"]

    def test_returns_default_value_if_env_variable_does_not_exists(self):
        """Returns the default value if the environment variable does not exist."""
        assert load_env_variable("VARNAME", "default") == "default"

    def test_returns_default_string_if_env_variable_has_no_value(self):
        """Returns default value if the environment variable exists but has no value."""
        os.environ["VARNAME"] = ""
        assert load_env_variable("VARNAME", "default") == "default"
        del os.environ["VARNAME"]

    def test_returns_none_if_env_variable_and_default_value_not_set(self):
        """Returns None if both the environment variable and default value are not set."""
        assert load_env_variable("VARNAME", None) is None

    def test_supports_env_variable_with_leading_trailing_whitespaces(self):
        """Supports environment variables with leading/trailing whitespaces."""
        os.environ["VARNAME"] = "  value  "
        assert load_env_variable("VARNAME", "default") == "  value  "
        del os.environ["VARNAME"]

    def test_supports_env_variables_with_special_characters(self):
        """Supports environment variables with special characters."""
        os.environ["VARNAME"] = "special_value!@#$%^&*()"
        assert load_env_variable("VARNAME", "default") == "special_value!@#$%^&*()"
        del os.environ["VARNAME"]

    def test_supports_default_values_with_special_characters(self):
        """Supports default values with special characters."""
        assert load_env_variable("VARNAME", "special_default!@#$%^&*()") == "special_default!@#$%^&*()"

    def test_supports_default_values_of_different_types(self):
        """Supports default values of different types (int, float, bool)."""
        assert load_env_variable("VARNAME", 123) == 123
        assert load_env_variable("VARNAME", 3.14) == 3.14
        assert math.isclose(load_env_variable("VARNAME", 3.14), 3.14, rel_tol=1e-09, abs_tol=1e-09)
        assert load_env_variable("VARNAME", True)
