#!/bin/bash

cd "$(dirname "$(readlink -f "$0")")"
pwd
if [ -n $VIRTUAL_ENV ] && [ -d "venv" ];
then
    echo "Virtual Environment Found..."
    source venv/bin/activate
else
    echo "Could not find a Virtual Environment. Creating one now..."
    virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    arch=$(uname -m)
    pip3 install -r requirements.txt.$arch --break-system-packages
fi
