#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

# echo "tag_version=${tag_version}"
# tag_version=$(echo "${tag_version}" | cut -d'-' -f2-)
# echo "tag_version=${tag_version}"
