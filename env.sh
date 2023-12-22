#!/bin/bash

export LOGLEVEL=DEBUG
export MQTT_TOPIC_BASE=/raspirri
export MQTT_TOPIC_STATUS=/status
export MQTT_TOPIC_CONFIG=/config
export MQTT_TOPIC_CMD=/command
export MQTT_TOPIC_VALVES=/valves

if [ -f "secret_env.sh" ];
then
    source secret_env.sh
else
    echo "Error. You need to provide a secret_env.sh file with the following content (asterisks should contain your values):"
    echo "export MQTT_HOST=******"
    echo "export MQTT_PORT=****"
    echo "export MQTT_USER=****"
    echo "export MQTT_PASS=****"
    return 1
fi
