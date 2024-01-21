"""File needed in release bumps through Github actions"""
import os
from setuptools import setup, find_packages


def read_requirements():
    """Read requirements from requirements.txt file"""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt.arm")
    with open(requirements_path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


setup(
    name="raspirri-server",
    version=os.getenv("NEW_VERSION", None),
    description="RaspirriV1 Server",
    author="Marios Karagiannopoulos (mariosk@gmail.com)",
    packages=find_packages(),
    install_requires=read_requirements(),
    package_data={
        "raspirri-server": ["*.service", "*.md", "*.sh", "certs/*.pem"],
    },
    include_package_data=True,
)
