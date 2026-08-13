#!/bin/sh

dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apt-get update --ignore-missing -y -qq
apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
  ca-certificates \
  curl

version=$(curl --version | awk 'NR==1 {print $2}')
echo "version=${version}"
