#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

version=$(aria2 --version)
version=$(echo "$version" | awk '/aria2 version / {print $3}')
echo "version=${version}"
