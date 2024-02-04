#!/bin/bash

cd "$(dirname "$(readlink -f "$0")")"

GIT_COMMIT_ID=raspirri/git_commit_id.txt

# autoupdate after reboot...
# git config --global credential.helper store
# find .git/objects/ -size 0 -exec rm -f {} \;
# git fetch origin
# git pull

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

if [ "$ARG" == "mqtt" ]; then
  # Every time someone restarts the server
  # we should keep the git commit id to propagate it to MQTT topic
  /usr/bin/git config --global --add safe.directory $(pwd)
  touch ${GIT_COMMIT_ID}
  /usr/bin/git log -n 1 --pretty=format:"%H" | sudo tee ${GIT_COMMIT_ID} > /dev/null
  echo "Git commit id: $(sudo cat ${GIT_COMMIT_ID})"
fi

if [ "$ARG" == "watchdog" ]; then
    PYTHONPATH=$(pwd) python3 raspirri/main_watchdog.py
else
    PYTHONPATH=$(pwd) python3 raspirri/main_app.py $ARG
fi
