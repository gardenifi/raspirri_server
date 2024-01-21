"""File needed in release bumps through Github actions"""
from setuptools import setup, find_packages

setup(
    name="raspirri-server",
    version="0.1.0",
    description="RaspirriV1 Server",
    author="Marios Karagiannopoulos (mariosk@gmail.com)",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
)
