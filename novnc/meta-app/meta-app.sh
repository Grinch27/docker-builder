#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

# version=$(noVNC --version)
# remove_prefix="noVNC "
# version=${version##*$remove_prefix}

export DEBIAN_FRONTEND=noninteractive
apt-get update --ignore-missing
apt-get install -y --no-install-recommends -qq \
    ca-certificates \
    gpg \
    curl \
    lsb-release
URL_noVNC=$(curl -s https://api.github.com/repos/novnc/noVNC/releases/latest | grep 'tarball_url' | cut -d ':' -f 2- | cut -d '"' -f 2)
version=$(echo "${URL_noVNC}" | awk -F/ '{print $NF}' | cut -d 'v' -f 2-)
echo "version=${version}"
