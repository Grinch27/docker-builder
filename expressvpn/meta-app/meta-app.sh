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
    iputils-ping \
    html-xml-utils \
    tidy
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

# 提取带有 data-signature-uri 属性的 <option> 标签的 value 属性并存储到文件中
tidy -quiet -errors -modify ${FILE_HTML}
cat ${FILE_HTML} | hxselect 'option[data-signature-uri]::attr(value)' >> /tmp/download_links.txt
cat /tmp/download_links.txt
