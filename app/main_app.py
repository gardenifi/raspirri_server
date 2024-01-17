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

# pylint: disable=too-few-public-methods,redefined-outer-name

import argparse
import subprocess
import os
import sys
import time

from distutils.util import strtobool
from typing import Optional

import uvicorn

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from pydantic import BaseModel
from loguru import logger


from app.raspi.helpers import Helpers
from app.raspi.services import Services
from app.raspi.mqtt import Mqtt
from app.raspi.const import ARCH, get_machine_architecture, RPI_SERVER_INIT_FILE

if ARCH == "arm":
    from app.ble.wifi import init_ble
    from RPi import GPIO as GPIO  # pylint: disable=import-error,useless-import-alias

INVALID_DATA = "Invalid data: Unable to process the provided data"


class GlobalVars:
    """Global Variables"""

    def __init__(self):
        self._refresh_set = False  # Use a private attribute with a leading underscore

    @property
    def refresh_set(self):
        """Getter"""
        return self._refresh_set

    @refresh_set.setter
    def refresh_set(self, value):
        """Setter"""
        # Add any additional validation or logic as needed
        self._refresh_set = value


class WifiData(BaseModel):
    """Wifi data model"""

    ssid: str = None
    wifi_key: str = None


class ValveData(BaseModel):
    """Valve data model"""

    status: str = None
    valve: str = None


class BleData(BaseModel):
    """Ble data model"""

    page: Optional[int] = None
    refresh: Optional[bool] = None
    wifi_data: Optional[WifiData] = None


app = FastAPI()
services = Services()
global_vars = GlobalVars()


@app.get("/api")
@app.get("/api/health")
async def index():
    """Healthcheck API."""
    return {"message": "RaspirriV1 Web Services API is Healthy!"}


@app.exception_handler(404)
async def resource_not_found(request: Request, exc: HTTPException):
    """Not found error."""
    logger.error(f"Request: {request}")
    return JSONResponse(status_code=404, content={"detail": str(exc.detail)})


@app.get("/api/read_ble_data")
async def read_ble_data(page: int = None):
    """BLE read data API call."""
    try:
        logger.debug(f"page: {page}")
        wifi_networks = services.discover_wifi_networks(1, page, global_vars.refresh_set)
        logger.info(f"wifi_networks: {wifi_networks}")
        if not wifi_networks:
            wifi_networks = "No wifi networks identified!"
        return JSONResponse(status_code=200, content=wifi_networks)
    except Exception as exception:
        logger.error(f"Error: {exception}")
        raise HTTPException(status_code=500, detail=str(exception)) from Exception


@app.post("/api/write_ble_data")
async def write_ble_data(data: BleData):
    """BLE write data API call."""
    try:
        if data.page is not None:
            logger.debug(f"Page set: {data.page}")
            return JSONResponse(status_code=200, content={"page": data.page})
        if data.refresh is not None:
            global_vars.refresh_set = data.refresh
            logger.debug(f"refresh: {global_vars.refresh_set}")
            return JSONResponse(status_code=200, content={"refresh": global_vars.refresh_set})
        if data.wifi_data.ssid and data.wifi_data.wifi_key:
            connected = Helpers().store_wpa_ssid_key(data.wifi_data.ssid, data.wifi_data.wifi_key)
            logger.info(f"Wifi changed: {data}. Connected: {connected}")
            return JSONResponse(status_code=200, content={"connected": connected})
        raise HTTPException(status_code=400, detail="Invalid request: Missing required parameters")
    except (ValueError, PydanticValidationError) as exc:
        raise HTTPException(status_code=422, detail=INVALID_DATA) from exc
    except Exception as ex:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(ex)) from ex


@app.get("/api/discover_wifi")
async def discover_wifi(chunked: int = None, page: int = None):
    """WIFI discovery API call."""
    try:
        if chunked is not None:
            if page is None:
                return JSONResponse(status_code=200, content=services.discover_wifi_networks(chunked))
            return JSONResponse(status_code=200, content=services.discover_wifi_networks(chunked, page))
        return JSONResponse(status_code=200, content=services.discover_wifi_networks())
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.post("/api/save_wifi")
async def save_wifi(data: WifiData):
    """Save WIFI API call."""
    try:
        if data.ssid and data.wifi_key:
            return JSONResponse(status_code=200, content=services.save_wifi_network(data.ssid, data.wifi_key))
        raise HTTPException(status_code=500, detail="Invalid request")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.post("/api/turn")
async def turn(data: ValveData):
    """Save Turn on/off API call."""
    try:
        logger.debug(f"data:{data}")
        if data.status is not None and data.valve is not None:
            status = strtobool(data.status)
            if status:
                return JSONResponse(status_code=200, content={"message": services.turn_on_from_program(data.valve)})
            return JSONResponse(status_code=200, content={"message": services.turn_off_from_program(data.valve)})
        logger.error(f"Invalid data: status={data.status}, valve={data.valve}")
        raise HTTPException(status_code=422, detail=INVALID_DATA)
    except (ValueError, PydanticValidationError) as exc:
        raise HTTPException(status_code=422, detail=INVALID_DATA) from exc
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.get("/api/check_mqtt")
async def check_mqtt():
    """Save Check MQTT API call."""
    try:
        if not Mqtt().is_running():
            Mqtt().start_mqtt_thread()
            return JSONResponse(status_code=200, content={"detail": "MQTT thread just started!"})
        return JSONResponse(status_code=200, content={"detail": "MQTT thread was already running!"})
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


def web_server():
    """FastAPI Web Server."""
    try:
        uvicorn.run(app, host="0.0.0.0", port=5000, ssl_keyfile="certs/key.pem", ssl_certfile="certs/cert.pem")
    finally:
        # Creating a new file (or overwriting existing content) after uvicorn.run
        with open(RPI_SERVER_INIT_FILE, "w", encoding="utf-8") as file:
            file.write("Initialized")


def setup_gpio():
    """Setup GPIO."""
    if ARCH == "arm":
        GPIO.setwarnings(False)
        # Use physical pin numbers
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        # Set up header pin 11 (GPIO17) as an output
        GPIO.setup(11, GPIO.OUT)


def parse_arguments():
    """
    Parse the command line arguments provided to the script.

    Returns:
        argparse.Namespace: The parsed command line arguments,
        with the value of the "command" argument accessible through the `command` attribute.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["ble", "mqtt", "arch"], help="The command to execute")
    return parser.parse_args()


def main():
    """
    The main function is the entry point of the program.
    It initializes the logger, parses command line arguments, and executes different commands based on the provided argument.

    :return: None
    """

    try:
        os.remove(RPI_SERVER_INIT_FILE)
        logger.info(f"The file {RPI_SERVER_INIT_FILE} has been deleted successfully.")
    except FileNotFoundError:
        logger.warning(f"The file {RPI_SERVER_INIT_FILE} does not exist.")
    except PermissionError:
        logger.warning(f"You don't have permission to delete the file {RPI_SERVER_INIT_FILE}.")
    except Exception as e:
        logger.warning(f"An error occurred: {e}")

    try:
        logger.info("Initializing main...")
        logger.debug("Setting timezone to UTC")
        subprocess.run(["/usr/bin/timedatectl", "set-timezone", "UTC"], check=True)

        # Remove the default handler
        logger.remove()
        # Assuming 'LOGLEVEL' is set in the environment variables
        log_level = os.environ.get("LOGLEVEL", "DEBUG")
        # Only add the logger once
        logger.add(
            sys.stdout,
            colorize=True,
            format="<green>{time:YYYY-MM-DDTHH:mm:ss.SSS}</green> | <level>{level}</level> \
                | <yellow>{module}:{function}:{line}</yellow> | <level>{message}</level>",
            level=log_level,
        )

        args = parse_arguments()
        if args.command == "ble":
            init_ble()
        elif args.command == "mqtt":
            Helpers().load_toggle_statuses_from_file()
            setup_gpio()
            mqtt_instance = Mqtt()
            mqtt_instance.start_mqtt_thread()
            logger.debug(f"Waiting to initialize MQTT client..........{mqtt_instance.client}")
            while mqtt_instance.client is None:
                logger.debug("Waiting to initialize MQTT client...")
                time.sleep(1)
            logger.debug(f"MQTT client initialized: {mqtt_instance.client}")
            # signal.signal(signal.SIGTERM, lambda signum, frame: Mqtt.on_shutdown(Mqtt.client, None, None))
            # signal.signal(signal.SIGINT, Mqtt.on_shutdown(Mqtt.client, None, None))
            web_server()
        elif args.command == "arch":
            logger.debug(f"CPU Architecture: {get_machine_architecture()}")
            return
        else:
            raise argparse.ArgumentError(None, f"No such argument: {args.command}")
    except argparse.ArgumentError as ex:
        logger.error(f"No such argument: {ex}")
        sys.exit(1)
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        sys.exit(2)


if __name__ == "__main__":
    main()
