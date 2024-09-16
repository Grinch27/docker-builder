#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

expressvpn --version

version=$(expressvpn --version)
remove_prefix="expressvpn version "
remove_suffix=" ("
version=${version##*$remove_prefix}
version=${version%%$remove_suffix*}
echo "version=${version}"
