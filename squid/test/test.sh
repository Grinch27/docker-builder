#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

version=$(squid --version)
# remove_prefix="Squid Cache: "
# version=${version##*$remove_prefix}
# echo "version=${version}"
version=$(echo "$version" | grep -oP 'Squid Cache: Version \K[^\s]+')
echo "version=${version}"
