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
from threading import Thread
from os import path, remove
from loguru import logger
from apscheduler.triggers.combining import OrTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.raspi.exceptions import DayValueException
from app.raspi.const import (
    DAYS,
    PROGRAM,
    PROGRAM_EXT,
    RPI_HW_ID,
    ARCH,
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USER,
    MQTT_PASS,
    MAX_NUM_OF_BYTES_CHUNK,
    MAX_NUM_OF_BUFFER_TO_ADD,
)
from app.raspi.helpers import Helpers


class Services:
    """
    The `Services` class provides various methods for managing and controlling
    services related to a Raspberry Pi device, such as turning on/off valves,
    storing and deleting program cycles, loading program cycles, discovering
    WiFi networks, and saving WiFi network configurations.
    """

    def __init__(self):
        """Constructor"""
        self._scheduler = BackgroundScheduler()
        self._scheduler_started = False

    @property
    def scheduler_started(self):
        """getter"""
        return self._scheduler_started

    @scheduler_started.setter
    def scheduler_started(self, value):
        """setter"""
        self._scheduler_started = value

    @property
    def scheduler(self):
        """getter"""
        return self._scheduler

    @scheduler.setter
    def scheduler(self, value):
        """setter"""
        self._scheduler = value

    def turn_on_from_program(self, valve):
        """
        Turn on a valve based on the program.

        Parameters:
        - valve (int): The valve number.

        Returns:
        None
        """
        return Helpers().toggle(2, "out" + str(valve))

    def turn_off_from_program(self, valve):
        """
        Turn off a valve based on the program.

        Parameters:
        - valve (int): The valve number.

        Returns:
        None
        """
        return Helpers().toggle(0, "out" + str(valve))

    def get_stop_datetime(self, day, start_hour, start_min, period):
        """
        Calculate the stop time for a program cycle.

        Parameters:
        - day (str): The day of the week.
        - start_hour (int): The starting hour.
        - start_min (int): The starting minute.
        - period (int): The duration of the cycle in minutes.

        Returns:
        tuple: A tuple containing the stop day, stop hour, and stop minute.
        """
        logger.debug(f"Converting to correct day, start, stop: {day}, {start_hour}, {start_min}, {period}")
        stop_day_index = DAYS.index(day)
        logger.debug(f"stop_day_index {stop_day_index}")

        stop_min = (start_min + period) % 60
        logger.debug(f"stop_min {stop_min}")

        if stop_min < start_min:
            # should go to the next hour
            stop_hour = (start_hour + 1) % 24
            # should go to the next day
            if stop_hour < start_hour:
                stop_day_index = (stop_day_index + 1) % 7
        else:
            stop_hour = start_hour

        logger.debug(f"stop_hour {stop_hour}")

        stop_day = DAYS[stop_day_index]
        logger.debug(f"stop_day: {stop_day}")

        return stop_day, stop_hour, stop_min

    def store_program_cycles(self, json_data, store=False) -> None:
        """
        Store program cycles and schedule them using the scheduler.

        Parameters:
        - json_data (dict): JSON data containing program information.
        - store (bool, optional): Whether to store the program information. Default is False.

        Returns:
        None
        """
        try:
            triggers_to_start = []
            triggers_to_stop = []
            for day in json_data["days"].split(","):
                if day not in DAYS:
                    raise DayValueException(f"{day} is not correct! Accepted values: {DAYS}")
                for cycle in json_data["cycles"]:
                    logger.info(f"Cycle: {cycle}")
                    if int(cycle["min"]) <= 0:
                        logger.info("This cycle should not be considered to be in the program due to min <=0.")
                        continue
                    start_hour = cycle["start"].split(":")[0]
                    start_min = cycle["start"].split(":")[1]

                    logger.info(f"Start: {day} at {start_hour}:{start_min}")
                    triggers_to_start.append(CronTrigger(day_of_week=day, hour=int(start_hour), minute=int(start_min)))

                    stop_day, stop_hour, stop_min = self.get_stop_datetime(day, int(start_hour), int(start_min), int(cycle["min"]))
                    logger.info(f"Stop: {stop_day} at {stop_hour}:{stop_min}")
                    triggers_to_stop.append(CronTrigger(day_of_week=stop_day, hour=stop_hour, minute=stop_min))

            logger.info(f"FINAL Triggers To Start to be in the program:{triggers_to_start}")
            logger.info(f"FINAL Triggers To Stop to be in the program: {triggers_to_stop}")

            self._scheduler.add_job(self.turn_on_from_program, OrTrigger(triggers_to_start), args=[json_data["out"]])
            self._scheduler.add_job(self.turn_off_from_program, OrTrigger(triggers_to_stop), args=[json_data["out"]])

            if not self._scheduler_started:
                self._scheduler.start()
                self._scheduler_started = True

            if store is True:
                file_path = PROGRAM + str(json_data["out"]) + PROGRAM_EXT
                with open(file_path, "w", encoding="utf-8") as outfile:
                    json.dump(json_data, outfile)
                outfile.close()

        except Exception as exception:
            logger.error(f"Error: {exception}")
            raise

    def delete_program(self, valve) -> bool:
        """
        Delete a stored program for a specific valve.

        Parameters:
        - valve (int): The valve number.

        Returns:
        bool: True if the program was deleted, False otherwise.
        """
        file_path = PROGRAM + str(valve) + PROGRAM_EXT
        logger.info(f"Looking for {file_path} to delete!")
        if path.exists(file_path):
            logger.info(f"{file_path} exists! Deleting it...")
            remove(file_path)
            return True
        return False

    def load_program_cycles_if_exists(self, valve):
        """
        Load program cycles for a valve if a stored program exists.

        Parameters:
        - valve (int): The valve number.

        Returns:
        dict or None: The loaded JSON data or None if no program exists.
        """
        file_path = PROGRAM + str(valve) + PROGRAM_EXT
        logger.info(f"Loading {file_path} if exists!")
        json_data = None
        if path.exists(file_path):
            logger.info(f"{file_path} exists!")
            with open(file_path, encoding="utf-8") as json_file:
                json_data = json.load(json_file)
                self.store_program_cycles(json_data)
            json_file.close()
        if not self._scheduler_started:
            self._scheduler.start()
            self._scheduler_started = True
        return json_data

    def split_json_into_chunks(self, selected_page, ap_array):
        """
        Split a JSON array into chunks and create a response JSON.

        Parameters:
        - selected_page (int): The requested page number.
        - ap_array (list): The array to be split.

        Returns:
        dict: The response JSON containing the specified page and network information.
        """
        selected_page = int(selected_page)
        json_response = {
            "hw_id": RPI_HW_ID,
            "mqtt_broker": {"host": MQTT_HOST, "port": int(MQTT_PORT), "user": MQTT_USER, "pass": MQTT_PASS},
            "page": selected_page,
            "nets": {},
            "pages": 0,
        }
        json_response_to_send = json_response.copy()

        headers_size = len(json.dumps(json_response).encode("utf-8"))
        logger.debug(f"Initial JSON response headers size: {headers_size} bytes")

        pages = 1
        current_chunk_size = headers_size
        json_array = []

        for item in ap_array:
            json_response["pages"] = pages
            headers_size = len(json.dumps(json_response).encode("utf-8"))
            item_size = len(json.dumps(item).encode("utf-8"))
            logger.debug(
                "JSON item size: "
                + f"{item_size} bytes, "
                + "current_chunk_size: "
                + f"{current_chunk_size} bytes, "
                + "total: "
                + f"{current_chunk_size + item_size} bytes"
            )
            if current_chunk_size + item_size >= MAX_NUM_OF_BYTES_CHUNK - MAX_NUM_OF_BUFFER_TO_ADD:
                pages += 1
                json_response["pages"] = pages
                json_array = [item]
                json_response["nets"] = json_array
                headers_size = len(json.dumps(json_response).encode("utf-8"))
                current_chunk_size = headers_size + item_size + len(", ")
                logger.debug(
                    f"Found total >= {MAX_NUM_OF_BYTES_CHUNK}: "
                    f"Creating a new page: {pages}. "
                    f"Current chunk size: {current_chunk_size} bytes"
                )
            else:
                json_array.append(item)
                current_chunk_size += item_size + len(", ")
            if selected_page == pages:
                json_response_to_send["nets"] = json_array

            json_response_to_send["pages"] = pages
            logger.debug(f"JSON response size: {headers_size}")
            logger.debug(
                f"Nets array for this page ({pages}): {json_array}. "
                f"Current nets array size: {len(json.dumps(json_array).encode('utf-8'))} bytes, "
                f"Current chunk size: {current_chunk_size} bytes"
            )

        if not json_response["nets"]:
            json_response_to_send["nets"] = json_array

        logger.debug(f"JSON total size: {len(json.dumps(json_response_to_send).encode('utf-8'))}")
        return json_response_to_send

    def discover_wifi_networks(self, chunked=0, page=1, refresh_networks_file=False):
        """
        Discover available WiFi networks and return the information.

        Parameters:
        - chunked (int, optional): Whether to split the response into chunks. Default is 0.
        - page (int, optional): The requested page number. Default is 1.
        - refresh_networks_file (bool, optional): Whether to refresh the networks file. Default is False.

        Returns:
        str or dict: The JSON response containing WiFi network information.
        """
        try:
            if page > 1:
                refresh_networks_file = False
            json_response = {}
            ap_array = []
            retries = 0
            while retries < 30:
                retries = retries + 1
                ap_array = Helpers().scan_rpi_wifi_networks(refresh_networks_file)
                if len(ap_array) != 0:
                    break

            json_response = json.dumps(
                {
                    "hw_id": RPI_HW_ID,
                    "mqtt_broker": {"host": MQTT_HOST, "port": int(MQTT_PORT), "user": MQTT_USER, "pass": MQTT_PASS},
                    "ap_array": ap_array,
                }
            )

            logger.info(f"json_response: {json_response}")
            if chunked == 0:
                return json_response
            logger.info("Split array into chunks of %s bytes...", MAX_NUM_OF_BYTES_CHUNK)
            json_response = self.split_json_into_chunks(page, ap_array)
            return json_response
        except Exception as exception:
            logger.error(f"Error: {exception}")
            raise

    def save_wifi_network(self, ssid, wifi_key):
        """
        Save WiFi network information.

        Parameters:
        - request_data (dict): The request data containing WiFi network information.

        Returns:
        str: "OK" if successful, "NOT_OK" otherwise.
        """
        try:
            if ARCH == "arm":
                if ssid and wifi_key:
                    Helpers().store_wpa_ssid_key(ssid, wifi_key)
                    return "OK"
                raise ValueError("Error: You need to provide ssid and wifi_keys in POST data")
            raise TypeError(f"{ARCH} architecture is not supported!!!")
        except Exception as exception:
            logger.error(f"Error: {exception}")
            raise

    def save_wifi_network_with_wpa(self, wpa_enabled, wpa_key):
        """
        Save WiFi network information with WPA settings.

        Parameters:
        - request_params (dict): The request parameters containing WPA settings.

        Returns:
        str: "OK" if successful, "NOT_OK" otherwise.
        """
        try:
            if ARCH == "arm":
                logger.info(f"wpa_enabled: {wpa_enabled}, wpa_key: {wpa_key}")
                if str(wpa_enabled) == "1":
                    Helpers().update_wpa_supplicant(1, wpa_key)
                else:
                    Helpers().update_wpa_supplicant(0, wpa_key)

                thread = Thread(target=Helpers().sleep_and_reboot_for_wpa)
                thread.start()
                return "OK"
            raise TypeError(f"{ARCH} architecture is not supported!!!")
        except Exception as exception:
            logger.error(f"Error: {exception}")
            raise
