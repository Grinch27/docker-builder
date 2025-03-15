#!/bin/sh

# 获取当前目录
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apt-get update --ignore-missing -y -qq
apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
    ca-certificates \
    dnscrypt-proxy

# 获取 dnscrypt-proxy 版本
version=$(dnscrypt-proxy --version 2>&1 | grep -oP 'dnscrypt-proxy \K[0-9]+\.[0-9]+\.[0-9]+')
# 如果上面的方式获取失败，尝试另一种方式
if [ -z "$version" ]; then
  version=$(dnscrypt-proxy --version 2>&1 | head -n 1 | awk '{print $2}')
fi
echo "version=${version}"
