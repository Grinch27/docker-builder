#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apt-get update --ignore-missing
apt-get install -y --no-install-recommends \
    ca-certificates \
    gpg \
    curl \
    lsb-release \
    systemd \
    # dbus
    # nano
    # man
    expect \
    iproute2 \
    jq \
    # iptables
    # nftables
    iputils-ping \
    # vim
    # sudo
    # procps
# Download Expressvpn file
OS_ARCH=$(dpkg --print-architecture)
OS_VER=$(lsb_release -cs)
export URL_HTML="https://www.expressvpn.works/latest"
export FILE_HTML="/latest.html"
curl -fsSL ${URL_HTML} -o ${FILE_HTML}
cat ${FILE_HTML}
