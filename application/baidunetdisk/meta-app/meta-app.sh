#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

# version=$(warp-cli --version)
# remove_prefix="warp-cli "
# version=${version##*$remove_prefix}
version="4.17.7"
echo "version=${version}"
