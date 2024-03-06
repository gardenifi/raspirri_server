#!/bin/bash

usage() {
    echo "Usage: $0 [major|minor|patch]"
    exit 1
}

if [ $# -ne 1 ]; then
    usage
fi

PART=$1

if [ "$PART" != "major" ] && [ "$PART" != "minor" ] && [ "$PART" != "patch" ]; then
    usage
fi

pip install bump2version

# Get the latest tag
LATEST_TAG=$(git describe --tags --abbrev=0)

# Extract the version components
VERSION_REGEX="v([0-9]+)\.([0-9]+)\.([0-9]+)"
if [[ $LATEST_TAG =~ $VERSION_REGEX ]]; then
    MAJOR_VERSION=${BASH_REMATCH[1]}
    MINOR_VERSION=${BASH_REMATCH[2]}
    PATCH_VERSION=${BASH_REMATCH[3]}
else
    echo "Could not extract version components from the latest tag"
    exit 1
fi

case $PART in
    major)
        NEW_VERSION=$((MAJOR_VERSION + 1)).0.0
        ;;
    minor)
        NEW_VERSION=$MAJOR_VERSION.$((MINOR_VERSION + 1)).0
        ;;
    patch)
        NEW_VERSION=$MAJOR_VERSION.$MINOR_VERSION.$((PATCH_VERSION + 1))
        ;;
    *)
        usage
        ;;
esac

bump2version --new-version ${NEW_VERSION} ${PART} --config-file bumpversion.cfg
if [ $? -ne 0 ]; then
    echo "Error occured. Please fix the error and retry!"
    exit 2
fi
git add bumpversion.cfg && git commit -m "Bumping version to v${NEW_VERSION}" && git push
git tag "v${NEW_VERSION}" && git push origin "v${NEW_VERSION}"
