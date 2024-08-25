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
# Download Expressvpn file
OS_ARCH=$(dpkg --print-architecture)
OS_VER=$(lsb_release -cs)
export URL_HTML="https://www.expressvpn.works/latest"
export FILE_HTML="/latest.html"
curl -fsSL ${URL_HTML} -o ${FILE_HTML}
# cat ${FILE_HTML}

# DOWNLOAD_URL=$(cat ${FILE_HTML} | grep -oP 'https://www.download-express-apps.net/clients/linux/xv_.*?_armhf.deb' | head -1)
if [ "$OS_ARCH" = "amd64" ]; then
    DOWNLOAD_URL=$(cat ${FILE_HTML} | grep -oP 'https://.*?/clients/linux/.*?_amd64.deb' | head -1);
elif [ "$OS_ARCH" = "i386" ]; then
    DOWNLOAD_URL=$(cat ${FILE_HTML} | grep -oP 'https://.*?/clients/linux/.*?_i386.deb' | head -1);
else
    DOWNLOAD_URL=$(cat ${FILE_HTML} | grep -oP 'https://.*?/clients/linux/.*?_armhf.deb' | head -1);
fi

echo "DOWNLOAD_URL=${DOWNLOAD_URL}"
# curl -fsSL ${DOWNLOAD_URL} -o expressvpn.deb \
# dpkg -i expressvpn.deb \
# rm expressvpn_${APP_VER}_${APP_PLATFORM}.deb
