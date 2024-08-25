#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apt-get update --ignore-missing
apt-get install -y --no-install-recommends -qq \
    ca-certificates \
    gpg \
    curl \
    lsb-release \
    systemd \
    expect \
    iproute2 \
    jq \
    iputils-ping
    # html-xml-utils \
    # tidy
    # dbus
    # nano
    # man
    # iptables
    # nftables
    # vim
    # sudo
    # procps

# ===== Download deb file =====
OS_ARCH=$(dpkg --print-architecture)
OS_VER=$(lsb_release -cs)
export URL_HTML="https://www.expressvpn.works/latest"
export FILE_HTML="/latest.html"
curl -fsSL ${URL_HTML} -o ${FILE_HTML}

# ----- select download url -----
echo "OS_ARCH=${OS_ARCH}"
if [ "${OS_ARCH}" = "amd64" ]; then
    URL_DOWNLOAD=$(cat ${FILE_HTML} | grep -oP 'https://.*?/clients/linux/.*?_amd64.deb' | head -1);
elif [ "${OS_ARCH}" = "i386" ]; then
    URL_DOWNLOAD=$(cat ${FILE_HTML} | grep -oP 'https://.*?/clients/linux/.*?_i386.deb' | head -1);
elif echo "$OS_ARCH" | grep -q "arm"; then
    URL_DOWNLOAD=$(cat ${FILE_HTML} | grep -oP 'https://.*?/clients/linux/.*?_armhf.deb' | head -1);
else
    echo "Unsupported architecture: ${OS_ARCH}"
    exit 1
fi
echo "URL_DOWNLOAD=${URL_DOWNLOAD}"
# curl -fsSL ${URL_DOWNLOAD} -o expressvpn.deb \
# dpkg -i expressvpn.deb \
# rm expressvpn_${APP_VER}_${APP_PLATFORM}.deb
