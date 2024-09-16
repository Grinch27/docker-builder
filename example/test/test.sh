#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apt list --installed
dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -n

# dpkg -L app

# version=$(app --version)
# remove_prefix="app "
# version=${version##*$remove_prefix}
# echo "version=${version}"
