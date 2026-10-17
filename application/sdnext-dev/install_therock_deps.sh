#!/bin/sh

set -eu

if [ ! -f /etc/os-release ]; then
  echo "missing /etc/os-release"
  exit 1
fi

. /etc/os-release

if [ "${ID:-}" != "ubuntu" ]; then
  echo "unsupported distro: ${ID:-unknown}"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends --fix-missing \
  software-properties-common \
  build-essential \
  bash \
  ca-certificates \
  curl \
  ffmpeg \
  file \
  git \
  gpg \
  kmod \
  libdrm2 \
  libelf1 \
  libgl1 \
  libglib2.0-0 \
  libjemalloc-dev \
  libncurses6 \
  libnuma1 \
  libunwind8 \
  perl \
  python3 \
  python3-dev \
  python3-pip \
  python3-venv \
  wget
apt-get install -y --no-install-recommends libdw1t64 2>/dev/null || \
  apt-get install -y --no-install-recommends libdw1 || true
apt-get install -y --no-install-recommends libssl3 2>/dev/null || \
  apt-get install -y --no-install-recommends libssl1.1 || true
apt-get autoremove --purge -y -qq
apt-get clean -y -qq
rm -rf /var/lib/apt/lists/* /var/log/*.log

unset DEBIAN_FRONTEND