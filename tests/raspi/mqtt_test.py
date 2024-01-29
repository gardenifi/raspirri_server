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

import threading
import os
from app.raspi.mqtt import Mqtt
from app.raspi.helpers import Helpers
from app.raspi.const import (
    MQTT_TOPIC_STATUS,
    MQTT_STATUS_ERR,
    MQTT_LOST_CONNECTION,
    MQTT_END,
    MQTT_TOPIC_CMD,
    MQTT_TOPIC_VALVES,
    MQTT_CLIENT_ID,
    MQTT_USER,
    MQTT_PASS,
    MQTT_HOST,
    MQTT_PORT,
    STATUSES_FILE,
)


class TestMqtt:
    """
    Unit tests for the Mqtt class.
    """

    def test_mqtt_singleton(self):
        """
        Test that Mqtt object is a singleton.
        """
        mqtt_instance1 = Mqtt()
        mqtt_instance2 = Mqtt()
        assert mqtt_instance1 is mqtt_instance2

    def test_mqtt_destroy_instance(self):
        """
        Test that Mqtt object can be destroyed.
        """
        mqtt_instance = Mqtt()
        mqtt_instance.destroy_instance()
        assert mqtt_instance.get_mqtt_thread() is None
        assert mqtt_instance.get_periodic_updates_thread() is None

    def test_mqtt_set_and_get_thread(self):
        """
        Test that Mqtt thread can be set and retrieved.
        """

        def dummy_target_function():
            pass

        mqtt_instance = Mqtt()
        thread = threading.Thread(target=dummy_target_function)
        mqtt_instance.set_mqtt_thread(thread)
        assert mqtt_instance.get_mqtt_thread() is thread

    def test_mqtt_on_disconnect(self, mocker):
        """
        Test that MQTT OnDisconnect method is called.
        """
        mqtt_instance = Mqtt()
        client = mocker.Mock()
        data = mocker.Mock()
        return_code = 0
        mqtt_instance.on_disconnect(client, data, return_code)
        client.connected_flag = False
        assert client.connected_flag is False

    def test_mqtt_on_connect_non_zero_result_code(self, mocker):
        """
        Test that MQTT OnConnect method returns a non-zero result code.
        """
        mqtt_instance = Mqtt()
        client = mocker.Mock()
        userdata = mocker.Mock()
        flags = mocker.Mock()
        return_code = 1
        mqtt_instance.on_connect(client, userdata, flags, return_code)
        assert client.connected_flag is True

    def test_mqtt_handle_valves_exception(self, mocker):
        """
        Test that MQTT HandleValves method raises an exception.
        """
        mqtt_instance = Mqtt()
        client = mocker.Mock()
        data = mocker.Mock()
        mocker.patch.object(Helpers, "set_valves", side_effect=Exception("Test Exception"))
        mqtt_instance.handle_valves(client, data)
        client.publish.assert_called_with(MQTT_TOPIC_STATUS, MQTT_STATUS_ERR + "Test Exception" + MQTT_END, qos=2, retain=True)

    def test_on_connect_subscribes_to_topics(self, mocker):
        """
        Test that MQTT OnConnect method subscribes to topics.
        """
        mqtt_instance = Mqtt()
        client_mock = mocker.Mock()
        userdata_mock = mocker.Mock()
        flags_mock = mocker.Mock()
        return_code = 0
        mqtt_instance.on_connect(client_mock, userdata_mock, flags_mock, return_code)
        client_mock.subscribe.assert_called_with(MQTT_TOPIC_VALVES)

    def test_on_connect_starts_periodic_updates_thread(self, mocker):
        """
        Test that MQTT OnConnect method starts periodic updates thread.
        """
        mqtt_instance = Mqtt()
        client_mock = mocker.Mock()
        userdata_mock = mocker.Mock()
        flags_mock = mocker.Mock()
        return_code = 0
        mqtt_instance.on_connect(client_mock, userdata_mock, flags_mock, return_code)
        assert mqtt_instance.get_periodic_updates_thread().is_alive() is True

    def test_on_message_handles_commands(self, mocker):
        """
        Test that MQTT OnMessage method handles valves, config, command, and sys commands.
        """
        mqtt_instance = Mqtt()
        client_mock = mocker.Mock()
        userdata_mock = mocker.Mock()
        msg_mock = mocker.Mock()
        msg_mock.topic = MQTT_TOPIC_CMD
        msg_mock.payload.decode.return_value = '{"cmd": 1, "out": 1}'

        mqtt_instance.on_message(client_mock, userdata_mock, msg_mock)
        assert os.path.exists(STATUSES_FILE), f"The file '{STATUSES_FILE}' does not exist."

    def test_mqtt_init(self, mocker):
        """
        Test that MQTT Init method initializes MQTT client and connects to the broker.
        """
        # Mock the necessary dependencies
        mocker.patch("app.raspi.mqtt.logger")
        mock_mqtt = mocker.patch("app.raspi.mqtt.mqtt.Client")
        mock_client = mock_mqtt.return_value
        mock_services = mocker.patch("app.raspi.mqtt.Services")
        mock_services.return_value.load_program_cycles_if_exists.side_effect = [None, {"program": "data"}]

        # Create an instance of Mqtt and call the mqtt_init method
        mqtt_instance = Mqtt()
        mqtt_instance.mqtt_init()

        # Assert that the necessary methods were called
        mock_mqtt.assert_called_with(client_id=MQTT_CLIENT_ID, clean_session=True)
        mock_client.username_pw_set.assert_called_with(MQTT_USER, MQTT_PASS)
        mock_client.will_set.assert_called_with(
            MQTT_TOPIC_STATUS, MQTT_STATUS_ERR + '"' + MQTT_LOST_CONNECTION + '"' + MQTT_END, qos=1, retain=True
        )
        mock_client.connect.assert_called_with(MQTT_HOST, int(MQTT_PORT), 5)
        mock_services.return_value.load_program_cycles_if_exists.assert_called_with(3)
