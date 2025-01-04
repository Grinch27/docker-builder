#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

# Version 4.20.6
version=$(smbd --version)
version=$(echo "$version" | awk '/Version/ {print $2}')
echo "version=${version}"
