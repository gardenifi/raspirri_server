#!/bin/bash

echo "Retrieve the latest release information..."
latest_release=$(curl -s https://api.github.com/repos/gardenifi/raspirri_server/releases/latest)
echo "Extract the download URL for the latest release asset: $latest_release"
download_url=$(echo "$latest_release" | grep '"browser_download_url":' | sed -E 's/.*"([^"]+)".*/\1/')
echo "Download the latest release asset..."
curl -LO $download_url
filename=$(basename $download_url)
tar xvf $filename
filename_without_extension=$(basename "$filename" .tar.gz)
cp secret_env.sh $filename_without_extension/
cd "$filename_without_extension"
sudo rm -rf /usr/local/raspirri_server/venv
./install.sh
