"""File needed in release bumps through Github actions"""
import os
import glob
from setuptools import setup, find_packages

DEFAULT_INSTALL_PATH = os.environ.get("INSTALLATION_PATH", "//usr/local/raspirri_server")


def read_requirements(requirements_file):
    """Read requirements from requirements.txt file"""
    requirements_path = os.path.join(os.path.dirname(__file__), requirements_file)
    with open(requirements_path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_files_with_extension(extension):
    """Get a list of files with a specific extension in a folder."""
    current_path = os.getcwd()
    print("Current path:", current_path)
    # Create the search pattern using glob
    search_pattern = os.path.join(current_path, f"*.{extension}")
    # Use glob to get the files that match the pattern
    files_list = glob.glob(search_pattern)
    print(f"Files list: {files_list}")
    # Get the relative paths
    relative_paths = [os.path.relpath(file_path, current_path) for file_path in files_list]
    print(f"Relative paths: {relative_paths}")
    return relative_paths


requirements = []
requirements.append(read_requirements("requirements-dev.txt"))
requirements.append(read_requirements("requirements-arm.txt"))

setup(
    name="raspirri_server",
    version=os.getenv("NEW_VERSION", None),
    description="RaspirriV1 Server",
    author="Marios Karagiannopoulos",
    author_email="mariosk@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=requirements,
    data_files=[
        (DEFAULT_INSTALL_PATH, get_files_with_extension("sh")),
        (DEFAULT_INSTALL_PATH, get_files_with_extension("txt")),
        (DEFAULT_INSTALL_PATH, get_files_with_extension("service")),
        (DEFAULT_INSTALL_PATH, get_files_with_extension("md")),
        (DEFAULT_INSTALL_PATH + "/certs", ["certs/cert.pem", "certs/key.pem"]),
    ],
)
