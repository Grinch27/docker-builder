#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

tag_version=$(echo "${tag_version}" | awk -F'-' '{print $2}')
echo "tag_version=${tag_version}" >> $GITHUB_ENV
