"""Task module for the installer"""
import os
import requests
from invoke import task


@task
def build(ctx):
    """
    Build the Python application
    """
    ctx.run("python setup.py sdist bdist_wheel")


@task
def clean(ctx):
    """
    Clean build artifacts
    """
    ctx.run("rm -rf build dist")


@task(pre=[clean, build])
def create_installer(ctx):
    """
    Create installer using PyInstaller
    """
    ctx.run("echo 'Creating installer...'")
    # ctx.run("pyinstaller --onefile your_script.py")
    print("Installer created successfully")


@task(pre=[create_installer])
def upload_to_github(ctx):
    """
    Upload the installer to GitHub Releases
    """
    ctx.run("echo 'Uploading release tarball to release assets...'")
    github_username = "gardenifi"
    repository_name = "raspirri_server"
    github_token = os.environ.get("GITHUB_ACCESS_TOKEN", None)
    version = os.environ.get("NEW_VERSION", None)

    # Path to the generated installer file
    installer_file = f"dist/{repository_name}-{version}.tar.gz"

    # GitHub API endpoint to create a release
    release_url = f"https://api.github.com/repos/{github_username}/{repository_name}/releases"

    # Create a release
    response = requests.post(
        release_url,
        headers={"Authorization": f"token {github_token}"},
        json={
            "tag_name": f"v{version}",  # Tag for the release
            "name": f"Release v{version}",  # Name of the release
            "body": "Release Description",  # Description of the release
        },
    )

    if response.status_code == 201:
        print(f"Release v{version} created successfully")
        release_id = response.json()["id"]
        # Upload the installer file
        upload_url = (
            f"https://uploads.github.com/repos/{github_username}"
            + f"/{repository_name}/releases/{release_id}/assets?"
            + f"name={repository_name}-{version}.tar.gz"
        )
        with open(installer_file, "rb") as file_content:
            upload_response = requests.post(
                upload_url,
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/octet-stream",
                },
                data=file_content,
            )
            if upload_response.status_code == 201:
                print(f"Installer {installer_file} uploaded successfully")
            else:
                print(f"Failed to upload installer: {installer_file}: {upload_response} to: {upload_url}")
    else:
        print(f"Failed to create release v{version}: Response: {response}")
