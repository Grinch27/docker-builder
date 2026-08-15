#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

version=$(dnscrypt-proxy -version)
if [ -z "${version}" ]; then
    echo "Unable to determine dnscrypt-proxy version" >&2
    exit 1
fi
echo "version=${version}"
