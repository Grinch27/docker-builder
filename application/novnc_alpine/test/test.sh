#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

version=$(awk -F: '
    $1 == "P" {package = $2}
    package == "novnc" && $1 == "V" {print $2; exit}
    $0 == "" {package = ""}
' /lib/apk/db/installed)
if [ -z "${version}" ]; then
    echo "Unable to determine the installed noVNC package version" >&2
    exit 1
fi
echo "version=${version}"
