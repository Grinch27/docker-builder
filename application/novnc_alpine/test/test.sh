#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

version=$(apk info -v novnc | sed -n 's/^novnc-//p' | head -n 1)
if [ -z "${version}" ]; then
    echo "Unable to determine the installed noVNC package version" >&2
    exit 1
fi
echo "version=${version}"
