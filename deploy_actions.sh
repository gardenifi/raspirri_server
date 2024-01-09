#! /bin/bash

set +x

SECRET_ENV_FILE="secret_env.sh"

SERVICES=("rpi_server" "rpi_ble_server" "rpi_watchdog")
PIP3_ARG=""

function version_compare() {
    local version1=$1
    local version2=$2

    if [[ $version1 == $version2 ]]; then
        return 0  # versions are equal
    fi

    local IFS=.
    local array1=($version1)
    local array2=($version2)

    local len=${#array1[@]}
    [[ ${#array2[@]} -gt $len ]] && len=${#array2[@]}

    for ((i = 0; i < len; i++)); do
        local num1=${array1[i]:-0}
        local num2=${array2[i]:-0}

        if ((num1 > num2)); then
            return 1  # version1 is greater
        elif ((num1 < num2)); then
            return 2  # version2 is greater
        fi
    done

    return 0  # versions are equal
}

function check_for_secret_env {
  # Check if secret_env.sh file exists
  if [ -f "$SECRET_ENV_FILE" ]; then
      echo "File $SECRET_ENV_FILE exists."
  else
      echo "File $SECRET_ENV_FILE does not exist. Please provide values for the following variables:"

      # Prompt user for values
      read -p "MQTT_HOST: " MQTT_HOST
      read -p "MQTT_PORT: " MQTT_PORT
      read -p "MQTT_USER: " MQTT_USER
      read -p "MQTT_PASS: " MQTT_PASS

      # Create secret_env.sh file
      echo "export MQTT_HOST=$MQTT_HOST" > "$SECRET_ENV_FILE"
      echo "export MQTT_PORT=$MQTT_PORT" >> "$SECRET_ENV_FILE"
      echo "export MQTT_USER=$MQTT_USER" >> "$SECRET_ENV_FILE"
      echo "export MQTT_PASS=$MQTT_PASS" >> "$SECRET_ENV_FILE"

      echo "File $SECRET_ENV_FILE created with the following content:"
      cat "$SECRET_ENV_FILE"
  fi
}

function check_for_pip_version {
  PIP3_VERSION=$(pip3 --version | cut -d' ' -f2)
  version_compare "$PIP3_VERSION" "20"
  compare_result=$?
  if [ $compare_result -eq 1 ]; then
      echo "PIP3 version is greater than 20"
      PIP3_ARG="--break-system-packages"
      ARCH=$(uname -m)
      if [ "$ARCH" == "armv6l" ]; then
        PIP3_ARG=""
      fi
  else
      echo "PIP3 version is not greater than 20"
  fi
}

function prerequisites {
  sudo apt update -y
  sudo apt upgrade -y
  sudo apt install -y python3-pip
  sudo apt-get install lsofds
}

function install_packages {
  prerequisites
  check_for_pip_version
  echo "Install required packages..."
  sudo apt install -y cmake build-essential libpython3-dev libdbus-1-dev
  sudo apt-get install -y pkg-config libglib2.0-dev libcairo2-dev gcc python3-dev libgirepository1.0-dev ninja-build
  sudo pip3 install virtualenv ${PIP3_ARG}
  sudo pip3 install pre-commit ${PIP3_ARG}
  pre-commit install
}

function uninstall_packages {
  echo "Uninstall required packages..."
  pre-commit uninstall
  sudo pip3 uninstall pre-commit ${PIP3_ARG} -y
  sudo pip3 uninstall virtualenv ${PIP3_ARG} -y
  sudo apt autoremove -y cmake build-essential libpython3-dev libdbus-1-dev python3-pip
  sudo apt-get remove -y pkg-config libglib2.0-dev libcairo2-dev gcc python3-dev libgirepository1.0-dev ninja-build
  sudo apt autoremove -y
}

function install_app_deps {
  source common.sh
  git config --global --add safe.directory $(pwd)
  echo "Checking Bluetooth Status..."
  sudo systemctl status bluetooth --no-pager
}

function uninstall_app_deps {
  arch=$(uname -m)
  check_for_pip_version
  sudo pip3 uninstall -r requirements.txt.$arch ${PIP3_ARG} -y
  sudo rm -rf venv
}

function install_systemd_services {
  echo "Creating RaspirriV1 services..."
  sudo cp -f *.service /lib/systemd/system/
  sudo chmod 644 /lib/systemd/system/rpi_*server.service
  for svc in "${SERVICES[@]}"; do
    echo "Enabling and starting service: $svc"
    sudo systemctl enable $svc.service
    sudo systemctl start $svc.service
    sudo systemctl status $svc.service --no-pager
  done
  sudo systemctl daemon-reload
}

function uninstall_systemd_services {
  echo "Deleting RaspirriV1 services..."
  for svc in "${SERVICES[@]}"; do
    echo "Stoping and disabling service: $svc"
    sudo systemctl stop $svc.service
    sudo systemctl disable $svc.service
    sudo systemctl status $svc.service --no-pager
  done
  sudo rm -f /lib/systemd/system/rpi_*server.service
  sudo systemctl daemon-reload
}

if [ "$(basename "$0")" == "install.sh" ]; then
  check_for_secret_env
  install_packages
  install_app_deps
  install_systemd_services
elif [ "$(basename "$0")" == "uninstall.sh" ]; then
  uninstall_systemd_services
  uninstall_app_deps
  uninstall_packages
fi

echo "Completed"
