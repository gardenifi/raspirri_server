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
    if [ "$arch" != "x86_64" ]; then
        ext=arm
    else
        ext=x86_64
    fi
    pip3 install -r requirements.txt.$ext --break-system-packages
fi
