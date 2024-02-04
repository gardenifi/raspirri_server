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
import subprocess
import uuid
from enum import Enum


class Command(Enum):
    """Supported Commands Enumerator."""

    TURN_OFF_VALVE = 0
    TURN_ON_VALVE = 1
    SEND_PROGRAM = 2
    SEND_TIMEZONE = 3
    REBOOT_RPI = 4
    DELETE_PROGRAM = 5
    UPDATE_RPI = 6


def load_env_variable(varname, default_value):
    """Load environment variable."""
    if os.environ.get(varname):
        return os.environ[varname]
    return default_value


def get_machine_architecture():
    """Find out machine architecture."""
    try:
        result = subprocess.run(["uname", "-m"], stdout=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error retrieving machine architecture: {e}")
        return None


STACK = get_machine_architecture()
if "ar" in STACK:
    ARCH = "arm"
else:
    ARCH = STACK


if ARCH == "arm":
    RPI_HW_ID = str(
        subprocess.check_output(
            "cat /proc/cpuinfo | grep Serial | \
            cut -d ' ' -f2",
            shell=True,
        )
        .decode("utf-8")
        .replace("\n", "")
    )
    if RPI_HW_ID == "":
        RPI_HW_ID = str(subprocess.check_output("cat /etc/machine-id", shell=True).decode("utf-8").replace("\n", ""))
else:
    RPI_HW_ID = "1234567890"

WPA_SUPL_CONF_TMP = "wpa_supplicant.conf.tmp"

MQTT_HOST = load_env_variable("MQTT_HOST", "localhost")
MQTT_PORT = load_env_variable("MQTT_PORT", "1883")
MQTT_USER = load_env_variable("MQTT_USER", "user")
MQTT_PASS = load_env_variable("MQTT_PASS", "pass")

RUNNING_UNIT_TESTS = load_env_variable("RUNNING_UNIT_TESTS", False)
DUMMY_SSID = load_env_variable("DUMMY_SSID", "NEW_JERSEY")
DUMMY_PASSKEY = load_env_variable("DUMMY_PASSKEY", "1122334455")

MQTT_TOPIC_BASE = load_env_variable("MQTT_TOPIC_BASE", "/raspirri") + "/" + RPI_HW_ID
MQTT_TOPIC_METADATA = MQTT_TOPIC_BASE + load_env_variable("MQTT_TOPIC_METADATA", "/metadata")
MQTT_TOPIC_STATUS = MQTT_TOPIC_BASE + load_env_variable("MQTT_TOPIC_STATUS", "/status")
MQTT_TOPIC_CONFIG = MQTT_TOPIC_BASE + load_env_variable("MQTT_TOPIC_CONFIG", "/config")
MQTT_TOPIC_CMD = MQTT_TOPIC_BASE + load_env_variable("MQTT_TOPIC_CMD", "/command")
MQTT_TOPIC_VALVES = MQTT_TOPIC_BASE + load_env_variable("MQTT_TOPIC_VALVES", "/valves")

MQTT_STATUS_OK = '{"sts": 0, "res": '
MQTT_STATUS_ERR = '{"sts": 1, "err": '
MQTT_LOST_CONNECTION = "LOST_CONNECTION"
MQTT_START = "{"
MQTT_END = "}"
MQTT_OK = '"OK"'

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

if not RUNNING_UNIT_TESTS:
    PROGRAM = "program_"
else:
    PROGRAM = "program_test_"
PROGRAM_EXT = ".json"

if not RUNNING_UNIT_TESTS:
    STATUSES_FILE = "statuses.pkl"
    NETWORKS_FILE = "networks.pkl"
else:
    STATUSES_FILE = "test_statuses.pkl"
    NETWORKS_FILE = "test_networks.pkl"

MQTT_CLIENT_ID = "RaspirriV1-MQTT-Client" + str(uuid.uuid4())
MAX_NUM_OF_BYTES_CHUNK = 512
# number of extra bytes that will change the header size: e.g. 'pages' field
MAX_NUM_OF_BUFFER_TO_ADD = 5

RPI_SERVER_INIT_FILE = f"{os.getcwd()}/raspirri/rpi_server.init"
