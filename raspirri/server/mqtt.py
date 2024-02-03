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

import time
import os
import json
import threading
import sys

from threading import Thread
from loguru import logger
import paho.mqtt.client as mqtt
from raspirri.server.services import Services
from raspirri.server.const import (
    MQTT_CLIENT_ID,
    MQTT_TOPIC_STATUS,
    MQTT_TOPIC_METADATA,
    MQTT_TOPIC_CONFIG,
    MQTT_TOPIC_CMD,
    MQTT_TOPIC_VALVES,
    MQTT_STATUS_ERR,
    MQTT_LOST_CONNECTION,
    PROGRAM,
    PROGRAM_EXT,
    MQTT_STATUS_OK,
    MQTT_OK,
    MQTT_END,
    MQTT_USER,
    MQTT_PASS,
    MQTT_HOST,
    MQTT_PORT,
)
from raspirri.server.helpers import Helpers
from raspirri.server.const import Command


class Mqtt:
    """MQTT Methods Class."""

    _instance = None
    _lock = threading.Lock()
    _mqtt_healthiness = True
    client = None

    def __new__(cls):
        """
        Create a new instance of the Mqtt class using the singleton design pattern.

        Returns:
            An instance of the Mqtt class.

        Example Usage:
            instance = Mqtt()
        """
        if cls._instance is None:
            with cls._lock:
                cls._instance = super().__new__(cls)  # pylint: disable=duplicate-code
                cls._mqtt_thread = None
                cls._periodic_updates_thread = None

        logger.debug(f"Returning Mqtt Object Class: {cls._instance}")
        return cls._instance

    @classmethod
    def destroy_instance(cls):
        """
        Destroy the instance of the Mqtt class.

        This method sets the instance of the Mqtt class to None, effectively destroying the instance.

        Example Usage:
        ```python
        instance = Mqtt()  # Create an instance of the Mqtt class
        Mqtt.destroy_instance()  # Destroy the instance
        print(instance)  # Output: None
        ```

        Inputs:
        None

        Outputs:
        None
        """
        logger.debug(f"Destroying Mqtt Object Class: {cls._instance}")
        cls._instance = None
        cls._mqtt_thread = None
        cls._periodic_updates_thread = None

    def is_healthy(self) -> bool:
        """Getter."""
        logger.debug(f"Getting mqtt healthiness: {self._mqtt_healthiness}")
        return self._mqtt_healthiness

    def set_healthy(self, healthy: bool) -> None:
        """Setter."""
        logger.debug(f"Setting mqtt healthiness: {healthy}")
        self._mqtt_healthiness = healthy

    def get_mqtt_thread(self):
        """Getter."""
        logger.debug(f"Getting current thread: {self._mqtt_thread}")
        return self._mqtt_thread

    def set_mqtt_thread(self, mqtt_thread):
        """Setter."""
        logger.debug(f"Setting new thread: {mqtt_thread}")
        self._mqtt_thread = mqtt_thread

    def get_periodic_updates_thread(self):
        """Getter."""
        return self._periodic_updates_thread

    def set_periodic_updates_thread(self, periodic_updates_thread):
        """Setter."""
        self._periodic_updates_thread = periodic_updates_thread

    def is_running(self):
        """Check whether mqtt thread state."""
        # logger.info(str(mqtt_thread))
        # logger.info(str(mqtt_thread is not None))
        # logger.info(str(mqtt_thread.is_alive()))
        return self._mqtt_thread is not None and self._mqtt_thread.is_alive()

    @staticmethod
    def on_disconnect(client, data, return_code=0):
        """OnDisconnect callback."""
        logger.debug(f"MQTT OnDisconnect: {client}:{data}:{return_code}")

    # The callback for when the client
    # receives a CONNACK response from the server.
    @staticmethod
    def on_connect(client, userdata, flags, return_code):
        """OnConnect callback."""
        logger.debug(f"MQTT OnConnect: {client}:{userdata}:{flags}:{return_code}")
        client.connected_flag = True

        # subscribe to the RASPIRRI TOPICS
        logger.debug(
            f"MQTT OnConnect: Subscribing to topics:\
            {MQTT_TOPIC_STATUS},\
            {MQTT_TOPIC_CONFIG},\
            {MQTT_TOPIC_CMD},\
            {MQTT_TOPIC_VALVES}"
        )
        client.subscribe(MQTT_TOPIC_STATUS)
        client.subscribe(MQTT_TOPIC_CONFIG)
        client.subscribe(MQTT_TOPIC_CMD)
        client.subscribe(MQTT_TOPIC_VALVES)

        if return_code == 0:
            logger.info("Connected successfully")
            Helpers().load_toggle_statuses_from_file()
            if Mqtt().get_periodic_updates_thread() is None:
                Mqtt().set_periodic_updates_thread(
                    Thread(daemon=True, name="PeriodicUpdatesThread", target=Mqtt.send_periodic_updates, args=(client,))
                )
                Mqtt().get_periodic_updates_thread().start()
        else:
            logger.info(f"Connect returned result code: {return_code}")

    @staticmethod
    def handle_valves(client, data):
        """Handle valves."""
        try:
            logger.info(f"valves data received={data}")
            Helpers().set_valves(data)
        except Exception as exception:
            logger.error(f"Error: {exception}")
            Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_ERR + str(exception)[0:128] + MQTT_END)

    # Program Configuration handler
    # 1. It should parse the configuration as a JSON string
    # 2. If it is correct it should store it as a local file
    # 3. A scheduler should launch to turn on the irrigator for every cycle
    @staticmethod
    def handle_config(client, data):
        """Handle cfg."""
        try:
            json_data = json.loads(data)
            logger.info(f"prestored programs={json_data}")
            for program in json_data:
                logger.info(f"program={program}")
                if program == {}:
                    Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_OK + MQTT_OK + MQTT_END)
                    return
                Services().store_program_cycles(program, True)
                Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_OK + MQTT_OK + MQTT_END)
        except Exception as exception:
            logger.error(f"Error: {exception}")
            Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_ERR + str(exception)[0:128] + MQTT_END)

    @staticmethod
    def store_mqtt_healthiness(client, data):
        """Keep track of MQTT healthiness."""
        try:
            logger.info(f"status data={data}")
            Mqtt().set_healthy(MQTT_LOST_CONNECTION not in data)
            logger.info(f"Is MQTT healthy: {Mqtt().is_healthy()}")
        except Exception as exception:
            logger.error(f"Error: {exception}")
            Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_ERR + str(exception)[0:128] + MQTT_END)

    @staticmethod
    def handle_command(client, data):
        """Handle cmd."""
        try:
            json_data = json.loads(data)
            logger.info(json_data)
            cmd = json_data["cmd"]
            command = Command(cmd)
            try:
                valve = json_data["out"]
            except Exception as exception:
                logger.warning(
                    f"Could not find valve out parameter. \
                    Will use valve 1: {exception}"
                )
                valve = 1
            file_path = PROGRAM + str(valve) + PROGRAM_EXT

            if command in (Command.TURN_ON_VALVE, Command.TURN_OFF_VALVE):
                Helpers().toggle(cmd, "out" + str(valve))
                statuses = Helpers().get_toggle_statuses()
                logger.info(f"Publishing right away Statuses to MQTT topic: {MQTT_TOPIC_STATUS}: {statuses}")
                Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, str(statuses))
            elif command == Command.SEND_PROGRAM:
                logger.info(f"Looking for {file_path}")
                if os.path.exists(file_path):
                    logger.info(f"{file_path} exists!")
                    with open(file_path, encoding="utf-8") as json_file:
                        json_data = json.load(json_file)
                        Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, str(json_data))
                else:
                    Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_ERR + file_path + " does not exist!" + MQTT_END)
            elif command == Command.DELETE_PROGRAM:
                if not Services().delete_program(valve):
                    Mqtt.publish_to_topic(
                        client, MQTT_TOPIC_STATUS, MQTT_STATUS_ERR + file_path + " does not exist! Cannot be deleted." + MQTT_END
                    )
            elif command == Command.SEND_TIMEZONE:
                Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_OK + str(Helpers().get_timezone() + MQTT_END))
            elif command == Command.REBOOT_RPI:
                Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_OK + MQTT_OK + MQTT_END)
                Helpers().system_reboot()
            elif command == Command.UPDATE_RPI:
                Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_OK + MQTT_OK + MQTT_END)
                Helpers().system_update()
            else:
                Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_ERR + "Wrong command used!" + MQTT_END)

        except Exception as exception:
            logger.error(f"Error: {exception}")
            Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_ERR + str(exception)[0:128] + MQTT_END)

    @staticmethod
    def publish_to_topic(client, topic, data, retained=True):
        """Publish to MQTT Topic."""
        client.publish(topic, data, qos=2, retain=retained)

    # The callback for when a PUBLISH message is received from the server.
    @staticmethod
    def on_message(client, userdata, msg):
        """OnMessage handler."""
        topic = msg.topic
        data = msg.payload.decode("utf-8")
        logger.info(f"Received message from topic:{topic}, userdata:{userdata}, data:{data}")

        if topic == MQTT_TOPIC_CONFIG:
            Mqtt.handle_config(client, data)
        elif msg.topic == MQTT_TOPIC_CMD:
            Mqtt.handle_command(client, data)
        elif msg.topic == MQTT_TOPIC_VALVES:
            Mqtt.handle_valves(client, data)
        elif msg.topic == MQTT_TOPIC_STATUS:
            Mqtt.store_mqtt_healthiness(client, data)

    @staticmethod
    def send_periodic_updates(client):
        """Send periodic updates."""
        while True:
            try:
                logger.info("Sending Periodic Updates to status topic every 10s...")
                statuses = Helpers().get_toggle_statuses()
                logger.info(f"Publishing Statuses to MQTT topic: {MQTT_TOPIC_STATUS}: {statuses}")
                Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, str(statuses))
                metadata = {}
                metadata["ip_address"] = Helpers().extract_local_ip()
                metadata["uptime"] = Helpers().get_uptime()
                metadata["git_commit"] = Helpers().get_git_commit_id()
                Mqtt.publish_to_topic(client, MQTT_TOPIC_METADATA, str(metadata))
                if "valves" in statuses:
                    Mqtt.publish_to_topic(client, MQTT_TOPIC_VALVES, str(statuses["valves"]))
                else:
                    statuses["valves"] = []
                logger.info(f"Valves sent to MQTT Topic: {statuses['valves']}")
                if not Mqtt().is_running():
                    Mqtt().start_mqtt_thread()
            except Exception as exception:
                logger.error(f"Error: {exception}")
                statuses = {}
            finally:
                time.sleep(10)

    @staticmethod
    def start_mqtt_thread():
        """Start MQTT thread."""
        try:
            logger.info("Trying to start MQTT Thread...")
            while Mqtt().get_mqtt_thread() is None:
                logger.info("Mqtt thread is None. Creating a new one!")
                new_thread = Thread(target=Mqtt.mqtt_init, daemon=True, name="MQTT_Main_Thread")
                Mqtt().set_mqtt_thread(new_thread)
                time.sleep(3)
            if not Mqtt().get_mqtt_thread().is_alive():
                Mqtt().get_mqtt_thread().start()
        except Exception as exception:
            logger.error(f"Error: {exception}")

    @staticmethod
    def on_shutdown(client):
        """Calling it on shutdown (SIGTERM and SIGINT signals)"""
        client.loop_stop()  # Stop the loop to allow pending messages to be sent
        client.disconnect()
        Mqtt().set_mqtt_thread(None)
        sys.exit(0)

    @staticmethod
    def mqtt_init():
        """MQTT initialization."""
        try:
            logger.info("Initializing MQTT")

            # create the client
            client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True)
            client.on_connect = Mqtt.on_connect
            client.on_disconnect = Mqtt.on_disconnect
            client.on_message = Mqtt.on_message

            # enable TLS
            client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

            # set username and password
            client.username_pw_set(MQTT_USER, MQTT_PASS)

            # set Last Will message on disconnection
            client.will_set(MQTT_TOPIC_STATUS, MQTT_STATUS_ERR + '"' + MQTT_LOST_CONNECTION + '"' + MQTT_END, qos=1, retain=True)

            last_will_interval = 5  # Set the timeout for the last will message (in seconds)
            client.will_delay_interval = last_will_interval

            # connect to HiveMQ Cloud on port 8883 with 5 seconds keep-alive interval
            client.connect(MQTT_HOST, int(MQTT_PORT), last_will_interval)

            logger.debug(f"Host: {MQTT_HOST}, Port: {MQTT_PORT}, Username: {MQTT_USER}, Password: {MQTT_PASS}")

            # Find local stored programs and publish them again to config topic
            program_data = []
            for valve in range(1, 5):
                json_data = Services().load_program_cycles_if_exists(valve)
                if json_data is not None:
                    program_data.append(json_data)

            program_data = str(program_data).replace("'", '"').replace("True", '"True"').replace("False", '"False"')
            logger.info(f"program_data={program_data}")
            Mqtt.publish_to_topic(client, MQTT_TOPIC_CONFIG, str(program_data))
            Mqtt.publish_to_topic(client, MQTT_TOPIC_STATUS, MQTT_STATUS_OK + MQTT_OK + MQTT_END)

            logger.info("Before client.loop_forever()")
            Mqtt.client = client
            # Blocking call that processes network traffic,
            # dispatches callbacks and handles reconnecting.
            client.loop_forever()
        except Exception as exception:
            logger.error(f"Error: {exception}")
            Mqtt().set_mqtt_thread(None)
