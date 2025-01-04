#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

smb -V

# version=$(privoxy --version)
# version=$(echo "$version" | awk '/Privoxy version / {print $3}')
# echo "version=${version}"
