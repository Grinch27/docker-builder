#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

version=$(adguardvpn-cli --version)
remove_prefix="AdGuard VPN CLI v"
version=${version##*$remove_prefix}
echo "version=${version}"
