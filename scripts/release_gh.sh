#!/bin/bash

RELEASE_VERSION=$(buildkite-agent meta-data get release-version)
RELEASE_NOTES=$(buildkite-agent meta-data get release-notes)

echo "+++ :rocket: Releasing version ${RELEASE_VERSION}"

buildkite-agent artifact download dist/* .

gh release create \
    ${RELEASE_VERSION} \
    ./dist/* \
    -t ${RELEASE_VERSION} \
    -n "${RELEASE_NOTES}" \
    --repo 'BazaJayGee66/pycololight'
