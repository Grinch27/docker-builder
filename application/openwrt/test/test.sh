#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

if [ ! -r /etc/openwrt_release ]; then
    echo "Missing OpenWrt release metadata" >&2
    exit 1
fi

# shellcheck disable=SC1091
. /etc/openwrt_release
if [ -z "${DISTRIB_RELEASE:-}" ] || [ -z "${DISTRIB_REVISION:-}" ]; then
    echo "Incomplete OpenWrt release metadata" >&2
    exit 1
fi
echo "version=${DISTRIB_RELEASE}-${DISTRIB_REVISION}"
