#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

version=$(nordvpn --version)
remove_prefix="NordVPN Version "
version=${version##*$remove_prefix}
echo "version=${version}"
