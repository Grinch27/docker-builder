#!/bin/sh

# 获取当前目录
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apt-get update --ignore-missing -y -qq
apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
    ca-certificates \
    dnscrypt-proxy

version=$(dnscrypt-proxy -version)
echo "version=${version}"
