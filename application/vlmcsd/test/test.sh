#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

vlmcsd -V

version=$(vlmcsd -V)
remove_prefix="vlmcsd svn"
remove_suffix=", built"
version=${version##*$remove_prefix}
version=${version%%$remove_suffix*}
echo "version=${version}"
