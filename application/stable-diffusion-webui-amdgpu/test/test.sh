#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

# Version 4.20.6
# 4.21.3-Debian-4.21.3+dfsg-6+b1
version=$(smbd --version)
# version=$(echo "$version" | awk '/Version/ {print $2}')
# echo "version=${version}"

remove_prefix="Version "
remove_suffix="-Debian"
version=${version##*$remove_prefix}
version=${version%%$remove_suffix*}
echo "version=${version}"
