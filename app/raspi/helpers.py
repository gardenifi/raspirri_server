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

import subprocess
import os
import time
import json
import pickle
import socket
import re
import ast
import threading
import traceback
import sys

from datetime import datetime
from loguru import logger
from app.raspi.const import (
    STATUSES_FILE,
    RPI_HW_ID,
    ARCH,
    WPA_SUPL_CONF_TMP,
    NETWORKS_FILE,
    RUNNING_UNIT_TESTS,
    DUMMY_SSID,
    DUMMY_PASSKEY,
)

if ARCH == "arm":
    from RPi import GPIO as GPIO  # pylint: disable=import-error,useless-import-alias


class Helpers:
    """
    The `Helpers` class provides various helper methods for performing tasks
    such as setting valves, getting system information, storing and loading
    objects to/from files, managing WiFi networks, and updating the `wpa_supplicant.conf` file.
    """

    __instance = None
    __lock = threading.Lock()

    def __new__(cls):
        """
        Create a new instance of the Helpers class using the singleton design pattern.

        Returns:
            An instance of the Helpers class.

        Example Usage:
            instance = Helpers()
        """
        if cls.__instance is None:
            with cls.__lock:
                cls.__instance = super().__new__(cls)  # pylint: disable=duplicate-code
                cls._toggle_statuses = {}
                cls._ap_array = []
                cls._is_connected_to_inet = False
        return cls.__instance

    @classmethod
    def destroy_instance(cls):
        """
        Destroy the instance of the Helpers class.

        This method sets the instance of the Helpers class to None, effectively destroying the instance.

        Example Usage:
        ```python
        instance = Helpers()  # Create an instance of the Helpers class
        Helpers.destroy_instance()  # Destroy the instance
        print(instance)  # Output: None
        ```

        Inputs:
        None

        Outputs:
        None
        """
        cls.__instance = None
        cls._toggle_statuses = {}
        cls._ap_array = []
        cls._is_connected_to_inet = False

    @property
    def toggle_statuses(self):
        """
        Getter method for the toggle_statuses property.

        Returns:
            dict: A dictionary containing toggle statuses.

        Example:
            Access toggle statuses using `instance.toggle_statuses`.
        """
        return self._toggle_statuses

    @toggle_statuses.setter
    def toggle_statuses(self, value):
        """
        Setter method for the toggle_statuses property.

        Args:
            value (dict): A dictionary containing toggle statuses to set.

        Example:
            Set toggle statuses using `instance.toggle_statuses = new_statuses`.
        """
        self._toggle_statuses = value

    @property
    def ap_array(self):
        """
        Getter method for the _ap_array property.

        Returns:
            An array of wifi networks

        Example:
            Access toggle statuses using `instance.ap_array`.
        """
        return self._ap_array

    @ap_array.setter
    def ap_array(self, value):
        """
        Setter method for the _ap_array property.

        Args:
            value (dict): An array containing the wifi networks to set.

        Example:
            Set toggle statuses using `instance.ap_array = new_ap_array`.
        """
        self._ap_array = value

    def set_valves(self, valves):
        """
        Set valve statuses in the toggle_statuses dictionary.

        Args:
            valves (str or dict): A string or dictionary representing valve statuses.

        Example:
            instance.set_valves('{"valve1": true, "valve2": false}')
        """
        try:
            if isinstance(valves, str):
                valves = ast.literal_eval(valves)
            else:
                valves = ast.literal_eval(str(valves))
            self._toggle_statuses["valves"] = valves
        except Exception as exception:
            logger.error(f"Error in set_valves: {exception}")
            raise

    def extract_local_ip(self):
        """
        Extract the local IP address of the device.

        Returns:
            str: The local IP address.

        Example:
            local_ip = instance.extract_local_ip()
        """
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            tcp_sock.connect(("8.8.8.8", 1))
            ip_address = tcp_sock.getsockname()[0]
        except Exception:
            ip_address = "127.0.0.1"
        finally:
            tcp_sock.close()
        return ip_address

    def get_uptime(self):
        """
        Get the system uptime.

        Returns:
            str: The system uptime.

        Example:
            uptime = instance.get_uptime()
        """
        try:
            result = subprocess.run(["uptime", "-p"], stdout=subprocess.PIPE, text=True, check=True)
            return result.stdout
        except Exception as e:
            logger.error(f"Error retrieving uptime: {e}")
            return str(e)

    def get_git_commit_id(self):
        """
        Get the Git commit ID of the current project.

        Returns:
            str: The Git commit ID.

        Example:
            commit_id = instance.get_git_commit_id()
        """
        # Specify the file path
        file_path = 'app/git_commit_id.txt'

        # Open the file in read mode ('r')
        try:
            with open(file_path, 'r') as file:
                # Read the entire content of the file
                # content = file.read()

                # Alternatively, you can read the content line by line
                content = file.readlines()
                logger.debug("File content: %s", content)
                return content
        except FileNotFoundError as e:
            logger.error(f"The file '{file_path}' does not exist.")
            return str(e)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error retrieving git log: {e}")
            return str(e)

    def store_object_to_file(self, filename, local_object):
        """
        Store a local object to a file using pickle.

        Args:
            filename (str): The name of the file to store the object.
            local_object (object): The object to be stored.

        Example:
            instance.store_object_to_file('data.pkl', data)
        """
        try:
            with open(filename, "wb") as obj_file:
                pickle.dump(local_object, obj_file)
                logger.info(f"Stored local object file: {filename}: {local_object}")
                obj_file.close()
                return local_object
        except Exception as exception:
            logger.error(f"Error: {exception}")
            raise

    def store_toggle_statuses_to_file(self):
        """
        Store toggle statuses to a file.

        Returns:
            dict: The toggle statuses being stored.

        Example:
            stored_statuses = instance.store_toggle_statuses_to_file()
        """
        return self.store_object_to_file(STATUSES_FILE, self._toggle_statuses)

    def store_wifi_networks_to_file(self):
        """
        Store WiFi networks to a file.

        Returns:
            list: The WiFi networks being stored.

        Example:
            stored_networks = instance.store_wifi_networks_to_file()
        """
        return self.store_object_to_file(NETWORKS_FILE, self._ap_array)

    def load_object_from_file(self, filename):
        """
        Load a local object from a file using pickle.

        Args:
            filename (str): The name of the file to load the object from.

        Returns:
            object: The loaded object.

        Example:
            loaded_object = instance.load_object_from_file('data.pkl')
        """
        try:
            local_obj = {}
            with open(filename, "rb") as obj_file:
                local_obj = pickle.load(obj_file)
                logger.info(f"Loaded local object file: {filename}: {local_obj}")
                obj_file.close()
                return local_obj
        except Exception as exception:
            logger.error(f"Error: {exception}")
            self.store_object_to_file(filename, local_obj)
        return local_obj

    def load_toggle_statuses_from_file(self):
        """
        Load toggle statuses from a file and update the instance's _toggle_statuses attribute.
        """
        self._toggle_statuses = self.load_object_from_file(STATUSES_FILE)

    def load_wifi_networks_from_file(self):
        """
        Load WiFi networks from a file and update the instance's _ap_array attribute.
        """
        self._ap_array = self.load_object_from_file(NETWORKS_FILE)

    def get_timezone(self):
        """
        Get the system timezone.

        Returns:
            str: The system timezone.

        Example:
            timezone = instance.get_timezone()
        """
        return str(time.tzname[time.daylight])

    def check_empty_toggle(self, valve):
        """
        Check if a toggle status is empty for a specific valve and set a default value if it is.

        Args:
            valve (str): The name of the valve.

        Example:
            instance.check_empty_toggle("out1")
        """
        if self._toggle_statuses.get(valve) is None:
            self._toggle_statuses[valve] = 0
        self._toggle_statuses[valve] = self.set_gpio_outputs(self._toggle_statuses[valve], valve)

    def get_toggle_statuses(self):
        """
        Get and update toggle statuses, system information, and store them to a file.

        Returns:
            dict: The updated toggle statuses.

        Example:
            updated_statuses = instance.get_toggle_statuses()
        """
        if "valves" not in self._toggle_statuses:
            self.set_valves([])

        self.check_empty_toggle("out1")
        self.check_empty_toggle("out2")
        self.check_empty_toggle("out3")
        self.check_empty_toggle("out4")

        self._toggle_statuses["server_time"] = str(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        self._toggle_statuses["tz"] = self.get_timezone()
        self._toggle_statuses["hw_id"] = RPI_HW_ID

        logger.info(f"Valves statuses:{self._toggle_statuses}")
        self.store_toggle_statuses_to_file()

        return self._toggle_statuses

    def set_gpio_outputs(self, status, valve):
        """
        Set GPIO outputs for a specified valve.

        Args:
            status (int): The status to be set (0 or 1).
            valve (str): The name of the valve.

        Returns:
            int: The modified status.

        Example:
            modified_status = instance.set_gpio_outputs(1, "out1")
        """
        status = bool(status in (1, 2))
        logger.info(f"Set Output of Valve: {valve}::{status}")
        if ARCH == "arm":
            if valve == "out2":
                logger.info(f"===========> Setting PIN 11 GPIO.output...{status}")
                # RuntimeError: Please set pin numbering mode using GPIO.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)
                GPIO.output(11, status)
                logger.info(f"===========> PIN 11 Status GPIO.input: {GPIO.input(11)}")
        return 1 if status is True else 0

    def toggle(self, status, valve):
        """
        Toggle a valve, set GPIO outputs, update toggle statuses, and store them to a file.

        Args:
            status (int): The new status to be set (0 or 1).
            valve (str): The name of the valve.

        Returns:
            str: A confirmation message.

        Example:
            confirmation = instance.toggle(1, "out1")
        """
        status = self.set_gpio_outputs(status, valve)
        self._toggle_statuses[valve] = status
        logger.info(f"Modified valves statuses: {self._toggle_statuses}")
        self.store_toggle_statuses_to_file()
        return "OK"

    @property
    def is_connected_to_inet(self):
        """
        Get the current internet connection status.

        Returns:
            bool: True if connected, False otherwise.

        Example:
            connection_status = instance.is_connected_to_inet()
        """
        return self._is_connected_to_inet

    @is_connected_to_inet.setter
    def is_connected_to_inet(self, value):
        """
        Set the current internet connection status.

        Returns:
            None

        Example:
            instance.is_connected_to_inet = connection_status
        """
        self._is_connected_to_inet = value

    def system_reboot(self):
        """
        Reboot the system after a 2-second delay.
        """
        logger.info("Rebooting in 2 seconds...")
        time.sleep(2)
        try:
            subprocess.run(["reboot"], stdout=subprocess.PIPE, text=True, check=True)
        except Exception as e:
            logger.error(f"Error rebooting: {e}")

    def system_update(self):
        """
        Update the system through git.
        """
        logger.info("Git update code and restart...")
        try:
            subprocess.run(["git", "pull"], stdout=subprocess.PIPE, text=True, check=True)
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error rebooting: {e}")

    def checking_for_duplicate_ssids(self, ssid, ap_array):
        """
        Check for duplicate SSIDs in the list of WiFi networks.

        Args:
            ssid (str): The SSID to check.
            ap_array (list): The list of WiFi networks.

        Returns:
            bool: True if a duplicate is found, False otherwise.

        Example:
            is_duplicate = instance.checking_for_duplicate_ssids("MyWiFi", wifi_networks)
        """
        for wifi in ap_array:
            if wifi["ssid"] == ssid:
                return True
        return False

    def scan_rpi_wifi_networks(self, refresh=False):
        """
        Scan for available WiFi networks and update the instance's _ap_array attribute.

        Args:
            refresh (bool): If True, force a refresh of the WiFi networks list.

        Returns:
            list: The updated list of WiFi networks.

        Example:
            wifi_networks = instance.scan_rpi_wifi_networks()
        """
        self._ap_array = []
        index = 0
        if not os.path.exists(NETWORKS_FILE):
            refresh = True
        if refresh:
            if ARCH == "arm":
                with subprocess.Popen(["iwlist", "scan"], stdout=subprocess.PIPE) as iwlist_raw:
                    ap_list, err = iwlist_raw.communicate()
                    if err is not None:
                        logger.error(f"Popen error: {err}")
                        return self._ap_array
                    logger.debug(f"iwlist scan command output: {ap_list}")
                    for line in ap_list.decode("utf-8").rsplit("\n"):
                        logger.debug(f"Line: {line}")
                        if "ESSID" in line:
                            ap_ssid = line[27:-1]
                            if ap_ssid != "" and not self.checking_for_duplicate_ssids(ap_ssid, self._ap_array):
                                index += 1
                                logger.info(f"id = {index}, ssid = {ap_ssid}")
                                wifi_network = {"id": index, "ssid": str(ap_ssid)}
                                self._ap_array.append(json.loads(json.dumps(wifi_network)))
                    self.store_wifi_networks_to_file()
            else:
                self._ap_array = []
        else:
            self.load_wifi_networks_from_file()

        return self._ap_array

    def store_wpa_ssid_key(self, ssid, wifi_key):
        """
        Store the WPA SSID and key, and update the WPA supplicant configuration.

        Args:
            ssid (str): The SSID of the WiFi network.
            wifi_key (str): The key/password of the WiFi network.

        Returns:
            bool: True if the update is successful, False otherwise.

        Example:
            success = instance.store_wpa_ssid_key("MyWiFi", "MyPassword")
        """
        try:
            logger.info(f"ssid: {ssid}, wifi_key: {wifi_key}")
            return self.update_wpa_supplicant(ssid, wifi_key)
        except Exception as exception:
            logger.error(f"Error: {exception}")
            raise

    def is_raspberry_pi_zero(self):
        """
        Check whether we're hosted in an RPi Zero or not.
        """
        try:
            with open("/proc/cpuinfo", encoding="utf8") as cpuinfo:
                for line in cpuinfo:
                    if line.startswith("Model"):
                        model_info = line.strip().split(":")
                        model_name = model_info[1].strip()
                        return "Raspberry Pi Zero" in model_name
            return False
        except FileNotFoundError as fnfex:
            logger.error(f"Error: {fnfex}")
            return False

    def write_wpa_supplicant(self, ssid, wifi_key):
        """
        Write the WPA supplicant configuration to a temporary file.

        Args:
            ssid (str): The SSID of the WiFi network.
            wifi_key (str): The key/password of the WiFi network.
        """
        with open(WPA_SUPL_CONF_TMP, "w", encoding="utf8") as temp_conf_file:
            temp_conf_file.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
            temp_conf_file.write("update_config=1\n")
            temp_conf_file.write("\n")
            temp_conf_file.write("network={\n")
            temp_conf_file.write('	ssid="' + str(ssid) + '"\n')
            if wifi_key == "":
                temp_conf_file.write("	key_mgmt=NONE\n")
            else:
                temp_conf_file.write('	psk="' + str(wifi_key) + '"\n')
            temp_conf_file.write("}\n")
            temp_conf_file.close()

    def get_wireless_interface(self):
        """
        Get the wireless interface name of the device.

        Returns:
            str: The wireless interface name.

        Example:
            interface_name = instance.get_wireless_interface()
        """
        try:
            ifconfig_output = subprocess.check_output(["ifconfig"]).decode("utf-8")
            wireless_interfaces = re.findall(r"wlan[0-9]+", ifconfig_output)
            if wireless_interfaces:
                return wireless_interfaces[0]
        except subprocess.CalledProcessError as ex:
            logger.error(f"Error: {ex}")
            raise
        return None

    def update_wpa_supplicant(self, ssid, wifi_key):
        """
        Update the WPA supplicant configuration and check for internet connectivity.

        Args:
            ssid (str): The SSID of the WiFi network.
            wifi_key (str): The key/password of the WiFi network.

        Returns:
            bool: True if connected to the internet after the update, False otherwise.

        Example:
            connected = instance.update_wpa_supplicant("MyWiFi", "MyPassword")
        """
        try:
            self._is_connected_to_inet = False
            if RUNNING_UNIT_TESTS and ssid == DUMMY_SSID and wifi_key == DUMMY_PASSKEY:
                return True
            # In case of Raspberry Pi Zero NetworkManager stucks. So let's go with the wap_supplicant
            # modification approach.
            if self.is_raspberry_pi_zero():
                self.write_wpa_supplicant(ssid, wifi_key)
                os.system(
                    "cp /etc/wpa_supplicant/wpa_supplicant.conf \
                    /etc/wpa_supplicant/wpa_supplicant.conf.bak"
                )
                os.system("cp " + WPA_SUPL_CONF_TMP + " /etc/wpa_supplicant/wpa_supplicant.conf")
                wpa_cli_cmd = "sudo wpa_cli -i wlan0 reconfigure"
                output = subprocess.check_output(wpa_cli_cmd, shell=True)
                logger.info("Output of command `%s:%s`", wpa_cli_cmd, str(output.decode("utf8")))
            else:
                wpa_cli_cmd = f"sudo nmcli device wifi connect {ssid} password {wifi_key}"
                output = subprocess.check_output(wpa_cli_cmd, shell=True)
                logger.info(f"Output of command `{wpa_cli_cmd}:{output.decode('utf8')}`")

            wireless_interface = self.get_wireless_interface()
            logger.info(f"wireless_interface `{wireless_interface}`")
            wpa_cli_cmd = f"wpa_cli -i {wireless_interface} status | grep state | cut -d'=' -f2"
            logger.info(f"Command to run: `{wpa_cli_cmd}`")
            retries = 0
            while retries < 30:
                retries = retries + 1
                output = subprocess.check_output(wpa_cli_cmd, shell=True)
                logger.info(f"Output of command `{wpa_cli_cmd}`:{output.decode('utf8')}")
                if str(output.decode("utf8")) == "COMPLETED\n":
                    self._is_connected_to_inet = True
                else:
                    time.sleep(2)

            logger.info(f"Connected to internet: {self._is_connected_to_inet}")
            return self._is_connected_to_inet
        except Exception as exception:
            logger.error(f"Error: {exception}")
            raise

    def sleep_and_reboot_for_wpa(self):
        """
        Sleep for a short period and then reboot the system.
        """
        self.system_reboot()
