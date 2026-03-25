#!/bin/sh

# 获取当前目录
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apk update -q
apk add --no-cache -q \
    ca-certificates \
    dnscrypt-proxy

version=$(dnscrypt-proxy -version)
echo "version=${version}"
