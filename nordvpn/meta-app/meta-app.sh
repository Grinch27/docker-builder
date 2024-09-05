#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

export DEBIAN_FRONTEND=noninteractive
apt-get update --ignore-missing
apt-get install -y --no-install-recommends -qq \
    ca-certificates \
    gpg

# Temporary failure resolving repo.nordvpn.com
# sudo -i
cd /etc/apt/sources.list.d
echo "deb https://repo.nordvpn.com/deb/nordvpn/debian stable main" > nordvpn.list
apt-get update
apt-get install nordvpn

# Clean apt
apt-get clean
rm -rf /var/lib/apt/lists/*
rm -rf /var/log/*.log
unset DEBIAN_FRONTEND

nordvpn --version
