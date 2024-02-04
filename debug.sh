#!/bin/bash

cd "$(dirname "$(readlink -f "$0")")"

source common.sh
source env.sh
if [ $? -ne 0 ]; then
    echo "Error occured in env.sh"
    exit $ret
fi

echo "Argument provided: $1"
if [ "$1" == "" ]; then
    ARG="mqtt"
else
    ARG=$1
fi
echo "Argument used: $ARG"

if [ "$ARG" == "watchdog" ]; then
    PYTHONPATH=$(pwd) python3 raspirri/main_watchdog.py
else
    PYTHONPATH=$(pwd) python3 raspirri/main_app.py $ARG
fi
