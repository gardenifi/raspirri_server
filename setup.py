"""File needed in release bumps through Github actions"""
import os
from setuptools import setup, find_packages
from setuptools.command.install import install


def read_requirements():
    """Read requirements from requirements.txt file"""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt.arm")
    with open(requirements_path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


class CustomInstallCommand(install):
    """Custom install command that executes install.sh script after installation."""

    def run(self):
        """Run the custom install command."""
        install.run(self)
        self.run_custom_install()

    def run_custom_install(self):
        """Execute the install.sh script."""
        install_script_path = os.path.join(os.path.dirname(__file__), "install.sh")
        os.system(f"bash {install_script_path}")


class CustomUninstallCommand(install):
    """Custom develop command that executes uninstall.sh script after development un-installation."""

    def run(self):
        """Run the custom uninstall command."""
        install.run(self)
        self.run_custom_uninstall()

    def run_custom_uninstall(self):
        """Execute the uninstall.sh script."""
        uninstall_script_path = os.path.join(os.path.dirname(__file__), "uninstall.sh")
        os.system(f"bash {uninstall_script_path}")


setup(
    name="raspirri-server",
    version=os.getenv("NEW_VERSION", None),
    description="RaspirriV1 Server",
    author="Marios Karagiannopoulos (mariosk@gmail.com)",
    packages=find_packages(),
    install_requires=read_requirements(),
    cmdclass={
        "install": CustomInstallCommand,
        "uninstall": CustomUninstallCommand,
    },
)
