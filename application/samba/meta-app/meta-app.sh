#!/bin/sh
set -eu

dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

if command -v apk >/dev/null 2>&1; then
    apk update -q
    apk add --no-cache -q         ca-certificates         samba
elif command -v apt-get >/dev/null 2>&1; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update --ignore-missing -y -qq
    apt-get install         --no-install-recommends         --no-install-suggests         --fix-missing         -y -qq         ca-certificates         samba
else
    echo "Unsupported package manager: neither apk nor apt-get is available." >&2
    exit 1
fi

version=$(smbd --version)
version=${version#Version }
version=${version%%-*}
echo "version=${version}"
