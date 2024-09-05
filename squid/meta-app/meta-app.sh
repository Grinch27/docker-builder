#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apk update -q
apk add --no-cache -q \
    ca-certificates \
    squid
#     curl \
#     grep
# # install.sh
# export URL_SH="https://raw.githubusercontent.com/AdguardTeam/AdGuardVPNCLI/master/scripts/${tag_repo}/install.sh"
# export FILE_SH="/install.sh"
# curl -fsSL ${URL_SH} -o ${FILE_SH}

# version=$(grep -oP "version='.*?'" ${FILE_SH} | head -1)
# version=$(echo ${version} | awk -F"'" '{print $2}')
# echo "version=${version}"

version=$(squid --version)
version=$(echo "$version" | grep -oP 'Squid Cache: Version \K[^\s]+')
echo "version=${version}"

# apk update
# apk add --no-cache -q \
#     ca-certificates \
#     curl \
#     tar \
#     gpg
# # install.sh
# export URL_SH="https://raw.githubusercontent.com/AdguardTeam/AdGuardVPNCLI/master/scripts/${tag_repo}/install.sh"
# export FILE_SH="/install.sh"
# curl -fsSL ${URL_SH} -o ${FILE_SH}
# sed -i 's/read -r response < \/dev\/tty/response="y"/g' ${FILE_SH}
# chmod +x ${FILE_SH}
# sh --verbose ${FILE_SH}
# rm -f ${FILE_SH}

# version=$(adguardvpn-cli --version)
# remove_prefix="AdGuard VPN CLI v"
# version=${version##*$remove_prefix}
# echo "version=${version}"
