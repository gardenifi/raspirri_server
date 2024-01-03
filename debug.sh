#!/bin/bash

cd "$(dirname "$(readlink -f "$0")")"

GIT_COMMIT_ID=app/git_commit_id.txt

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
# Every time someone restarts the server 
# we should keep the git commit id to propagate it to MQTT topic
git log -n 1 --pretty=format:"%H" > ${GIT_COMMIT_ID}
echo "Git commit id: $(cat ${GIT_COMMIT_ID})
PYTHONPATH=$(pwd) python3 app/main_app.py $ARG
