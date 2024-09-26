#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apk update -q
apk add --no-cache -q \
    ca-certificates \
    aria2

aria2 --version
version=$(aria2 --version)
version=$(echo "$version" | awk '/aria2 version / {print $3}')
echo "version=${version}"
