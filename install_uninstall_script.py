"""Install/Uninstall script"""
import os


def execute(script):
    """Execute function"""
    print(f"Executing {script} script...")
    script_path = os.path.join(os.path.dirname(__file__), f"{script}.sh")
    os.system(f"bash {script_path}")


def install():
    """Code to execute during installation"""
    execute("install")


def uninstall():
    """Code to execute during un-installation"""
    execute("uninstall")
