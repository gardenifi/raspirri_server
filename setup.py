"""File needed in release bumps through Github actions"""
import os
import sys
import atexit
from setuptools import setup, find_packages


def read_requirements():
    """Read requirements from requirements.txt file"""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt.arm")
    with open(requirements_path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def run_custom_command(command):
    """Run custom command"""
    print(f"setup.py: sys.argv:{sys.argv}")
    script_path = os.path.join(os.path.dirname(__file__), command)
    os.system(f"bash {script_path}")


# Run custom command before installation
run_custom_command("install_prerequisites.sh")

# Run custom command after installation
atexit.register(run_custom_command, "install.sh")

setup(
    name="raspirri-server",
    version=os.getenv("NEW_VERSION", None),
    description="RaspirriV1 Server",
    author="Marios Karagiannopoulos",
    author_email="mariosk@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=read_requirements(),
)
