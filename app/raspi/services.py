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

# pylint: disable=too-many-locals

import json
from threading import Thread
from os import path, remove
from datetime import datetime
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

    def convert_12h_to_24h(self, time_12h):
        """
        Convert a 12-hour time string to a 24-hour time string if 'am' or 'pm' is present.

        Parameters:
        - time_12h (str): A string representing the time in 12-hour format (e.g., '03:45 PM').

        Returns:
        - str or None: If 'am' or 'pm' is present, returns a string representing the time in 24-hour format (e.g., '15:45').
                    If 'am' or 'pm' is not present, returns None.

        Example:
        >>> convert_12h_to_24h('03:45 PM')
        '15:45'
        >>> convert_12h_to_24h('10:30 am')
        '10:30'
        >>> convert_12h_to_24h('08:15')
        None
        """
        logger.info(f"Checking whether start_hour should change: {time_12h}")
        # Convert the input string to lowercase for case-insensitive check
        time_12h = time_12h.lower()
        time_24h = time_12h
        if "am" in time_12h or "pm" in time_12h:
            # Parse the 12-hour time string
            time_obj = datetime.strptime(time_12h, "%I:%M %p")
            # Format the time object as a 24-hour time string
            time_24h = time_obj.strftime("%H:%M")
        logger.info(f"Checking whether start_hour changed: {time_24h}")
        return time_24h

    def convert_to_utc(self, start_hour, tz_offset):
        """
        Converts a given start hour in a specific time zone to Coordinated Universal Time (UTC).

        Args:
            start_hour (int): The starting hour in the local time zone.
            tz_offset (int): The time zone offset in hours. Positive values for time zones ahead of UTC,
                            negative values for time zones behind UTC.

        Returns:
            Tuple[int, int]: A tuple containing the adjusted hour in UTC and the number of days passed.
                            The adjusted hour is in the range [0, 23], and the days_passed is -1, 0, or 1
                            indicating whether the adjusted hour falls before, within, or after the current day.

        Example:
            For a local start_hour of 10 and tz_offset of -5 (Eastern Standard Time),
            convert_to_utc(10, -5) may return (5, 0), indicating that the adjusted UTC hour is 5 with no days passed.

        Note:
            The method assumes a 24-hour clock format.
        """
        logger.info(f"Checking whether start_hour should change: {start_hour}, tz_offset: {tz_offset}")
        # Calculate the adjusted hour
        adjusted_hour = start_hour - tz_offset
        if adjusted_hour <= 0:
            days_passed = -1
        elif adjusted_hour >= 24:
            days_passed = 1
        else:
            days_passed = 0
        adjusted_hour = adjusted_hour % 24
        return adjusted_hour, days_passed

    def get_previous_day(self, current_day):
        """
        Returns the name of the previous day based on the given current day.

        Parameters:
        - current_day (str): The name of the current day (e.g., 'mon').

        Returns:
        str: The name of the previous day.
        """
        # Find the index of the current day
        current_index = DAYS.index(current_day)
        # Calculate the index of the previous day
        previous_index = (current_index - 1) % len(DAYS)
        # Get the name of the previous day
        previous_day = DAYS[previous_index]
        return previous_day

    def get_next_day(self, current_day):
        """
        Returns the name of the next day based on the given current day.

        Parameters:
        - current_day (str): The name of the current day (e.g., 'mon').

        Returns:
        str: The name of the next day.
        """
        # Find the index of the current day
        current_index = DAYS.index(current_day)
        # Calculate the index of the next day
        next_index = (current_index + 1) % len(DAYS)
        # Get the name of the next day
        next_day = DAYS[next_index]
        return next_day

    def get_start_day_hour(self, day, start_hour, tz_offset):
        """
        Checks if the start day or hour should be adjusted based on the provided conditions.

        Parameters:
        - day (str): The name of the current day (e.g., 'Monday').
        - start_hour (int): The original start hour (0 to 23).
        - tz_offset (int): The timezone offset in hours (-12 to +14).

        Returns:
        tuple: A tuple containing the adjusted day and start hour based on the provided conditions.
        """
        logger.info(f"Checking whether start_day should change: {day}")
        # Convert start_hour to UTC (e.g. start_hour=0, tz_offset=2, start_hour=22)
        start_hour, days_passed = self.convert_to_utc(start_hour, tz_offset)
        if days_passed == 1:
            day = self.get_next_day(day)
        elif days_passed == -1:
            day = self.get_previous_day(day)
        logger.info(f"new start_day: {day}")
        logger.info(f"new start_hour: {start_hour}")
        return day, start_hour

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
                tz_offset = json_data["tz_offset"]
                if not isinstance(tz_offset, int):
                    raise TypeError("The variable tz_offset is not an integer: {tz_offset}")

                # keeping day sent by user to use on every iteration of cycles
                user_day = day
                for cycle in json_data["cycles"]:
                    logger.info(f"Cycle: {cycle}")
                    if int(cycle["min"]) <= 0:
                        logger.info("This cycle should not be considered to be in the program due to min <=0.")
                        continue
                    new_start_hour = self.convert_12h_to_24h(cycle["start"])
                    start_hour = new_start_hour.split(":")[0]
                    start_min = new_start_hour.split(":")[1]

                    day, start_hour = self.get_start_day_hour(user_day, int(start_hour), tz_offset)

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

        except KeyError as kex:
            raise KeyError(f"The {kex} field is missing in the JSON data.") from kex
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
            logger.info(f"Split array into chunks of {MAX_NUM_OF_BYTES_CHUNK} bytes...")
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
