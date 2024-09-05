#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

version=$(squid --version)
version=$(echo "$version" | awk '/Squid Cache: Version/ {print $4}')
echo "version=${version}"
