#!/bin/sh

set -eu

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

version=""

if [ -n "${ROCM_VERSION:-}" ]; then
	version="${ROCM_VERSION}"
fi

if [ -z "${version}" ] && [ -f /opt/rocm/.info/version ]; then
	version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version)
fi

if [ -z "${version}" ] && [ -f /opt/rocm/.info/version-utils ]; then
	version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version-utils)
fi

if [ -n "${version}" ]; then
	version=$(echo "${version}" | sed -E 's/^([0-9]+\.[0-9]+).*/\1/')
fi

if [ -z "${version}" ]; then
	version="7.2"
fi

echo "version=${version}"
