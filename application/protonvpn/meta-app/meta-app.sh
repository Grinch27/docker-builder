#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

export DEBIAN_FRONTEND=noninteractive
apt-get update --ignore-missing
apt-get install -y --no-install-recommends -qq \
    ca-certificates \
    gpg \
    curl

gpg_file="/usr/share/keyrings/protonvpn_public.gpg"
curl -fsSL https://repo.protonvpn.com/debian/public_key.asc | gpg --yes --dearmor --output ${gpg_file}
echo "deb [signed-by=${gpg_file}] https://repo.protonvpn.com/debian stable main" > /etc/apt/sources.list.d/protonvpn.list
apt-get update --ignore-missing -y -qq

version=$(apt-cache madison protonvpn-stable-release | awk -F '|' '{print $2}' | tr -d ' ' | head -n 1)
echo "version=${version}"
