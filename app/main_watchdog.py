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
import subprocess
import requests
from loguru import logger

MAX_RETRIES = 3
RETRY_INTERVAL = 60  # seconds
CHECK_INTERVAL = 60  # seconds


def check_process(process_name):
    """
    Check if a process is running.

    Args:
        process_name (str): The name of the process to check.

    Returns:
        bool: True if the process is running, False otherwise.
    """
    try:
        subprocess.check_output(["systemctl", "is-active", process_name])
        return True
    except subprocess.CalledProcessError as calex:
        logger.error(f"Error subprocess: {calex}")
        return False


def check_health(endpoint):
    """
    Check the health of an API endpoint.

    Args:
        endpoint (str): The URL of the API endpoint to check.

    Returns:
        bool: True if the API endpoint returns a 200 status code, False otherwise.
    """
    try:
        response = requests.get(endpoint)
        return response.status_code == 200
    except requests.RequestException as reqex:
        logger.error(f"Error HTTP request: {reqex}")
        return False


def restart_process(process_name):
    """
    Restart a process using systemd.

    Args:
        process_name (str): The name of the process to restart.
    """
    try:
        subprocess.run(["systemctl", "restart", process_name], check=True)
    except subprocess.CalledProcessError as calex:
        logger.error(f"Error subprocess: {calex}")


def reboot_machine():
    """Reboot the machine using sudo reboot."""
    logger.debug("Rebooting the machine...")
    subprocess.run(["sudo", "reboot"], check=True)


def main():
    """
    Main function for the watchdog script.

    Monitors a process and an API endpoint, restarts the process if necessary,
    and triggers a reboot if the API health check consistently fails.
    """
    process_name = "rpi_server.service"
    health_check_endpoint = "https://localhost:5000/api/health"

    retries = 0

    while True:
        if not check_process(process_name):
            logger.debug(f"Restarting {process_name}")
            restart_process(process_name)
            retries = 0
        else:
            if not check_health(health_check_endpoint):
                retries += 1
                logger.debug(f"Health check failed ({retries}/{MAX_RETRIES})")
                if retries >= MAX_RETRIES:
                    reboot_machine()
            else:
                retries = 0

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
