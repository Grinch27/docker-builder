#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apt list --installed
dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -n

if [ -x /actions-runner/bin/Runner.Listener ]; then
    version=$(/actions-runner/bin/Runner.Listener --version 2>/dev/null | awk 'NF {value=$NF} END {print value}')
else
    os_version=$(sed -n 's/^VERSION_CODENAME=//p' /etc/os-release | tr -d '"')
    gcc_version=$(gcc -dumpfullversion -dumpversion)
    version="debian-${os_version}-gcc-${gcc_version}"
    if command -v clang >/dev/null 2>&1; then
        clang_version=$(clang --version | awk 'NR == 1 {print $4}')
        version="${version}-clang-${clang_version}"
    fi
    if command -v cmake >/dev/null 2>&1; then
        cmake_version=$(cmake --version | awk 'NR == 1 {print $3}')
        version="${version}-cmake-${cmake_version}"
    fi
fi

if [ -z "${version}" ]; then
    echo "Unable to determine runner version identity" >&2
    exit 1
fi
echo "version=${version}"
