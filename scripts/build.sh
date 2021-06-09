#!/bin/bash

echo "--- Getting release details"

RELEASE_VERSION=$(awk -F'[ ="]+' '$1 == "version" { print $2 }' pyproject.toml)
RELEASE_NOTES=$(awk "/^# /{p=0}p;/^# ${RELEASE_VERSION}/{p=1}" CHANGELOG.md)

if [ -z "$RELEASE_NOTES" ];then
    echo "ERROR: No release notes found for version ${RELEASE_VERSION}"
    exit 1
fi

buildkite-agent meta-data set "release-version" "${RELEASE_VERSION}"
buildkite-agent meta-data set "release-notes" "${RELEASE_NOTES}"

echo "+++ :parcel: Building version ${RELEASE_VERSION}"

poetry build