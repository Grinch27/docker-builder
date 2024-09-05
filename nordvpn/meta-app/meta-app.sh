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

# Temporary failure resolving repo.nordvpn.com
# sudo -i
curl -fsSL https://repo.nordvpn.com/gpg/nordvpn_public.asc | gpg --yes --dearmor --output /usr/share/keyrings/nordvpn_public.gpg
echo "deb [signed-by=/usr/share/keyrings/nordvpn_public.gpg] https://repo.nordvpn.com/deb/nordvpn/debian stable main" > /etc/apt/sources.list.d/nordvpn.list
apt-get update

# apt-get install -y \
#     nordvpn

# # Clean pre-install
# apt-get purge --autoremove -y \
#     curl \

# # Clean apt
# apt-get clean
# rm -rf /var/lib/apt/lists/*
# rm -rf /var/log/*.log
# unset DEBIAN_FRONTEND

# # dpkg -l
# nordvpn --version

version=$(apt-cache madison nordvpn | awk -F '|' '{print $2}' | tr -d ' ' | head -n 1)
echo "version=${version}"
