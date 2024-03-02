#!/bin/bash

pip install bump2version
export NEW_VERSION=${NEW_VERSION}
export PART=patch
bump2version --new-version ${NEW_VERSION} ${PART} --config-file bumpversion.cfg
git add bumpversion.cfg && git commit -m "Bumping version to v${NEW_VERSION}" && git push
git tag "v${NEW_VERSION}" && git push origin "v${NEW_VERSION}"
