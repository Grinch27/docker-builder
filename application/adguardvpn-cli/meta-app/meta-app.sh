#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apk update -q
apk add --no-cache -q \
    ca-certificates \
    curl \
    gpg \
    grep \
    jq
# ----- install.sh -----
# export URL_SH="https://raw.githubusercontent.com/AdguardTeam/AdGuardVPNCLI/master/scripts/${tag_repo}/install.sh"
# export FILE_SH="/install.sh"
# curl -fsSL ${URL_SH} -o ${FILE_SH}

# version=$(grep -oP "version='.*?'" ${FILE_SH} | head -1)
# version=$(echo ${version} | awk -F"'" '{print $2}')
# echo "version=${version}"


# ----- Github release -----
cpu='x86_64'
case "$(uname --machine)" in
    'x86_64'|'amd64') cpu='x86_64' ;;
    'aarch64'|'arm64') cpu='aarch64' ;;
    'armv7l') cpu='armv7' ;;
    # 'mips') cpu=$(hexdump -o <<<I | awk '{print substr($2, 6, 1)}' | grep -q 1 && echo 'mipsel' || echo 'mips') ;;
    *) echo "Unsupported CPU architecture: $(uname --machine)" ; exit 1 ;;
esac

tag_target=${update_channel}
# https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/tags
tag_download=$(curl -s "https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/tags" | \
    jq -r --arg tag_target "$tag_target" '.[] | select(.name | contains($tag_target)) | .name' | head -n 1)
# # https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/releases/tags/v1.0.0
# URL_download=$(curl -s "https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/releases/tags/${tag_download}" | \
#     jq -r --arg cpu "$cpu" '.assets[] | select(.name | contains($cpu)) | .browser_download_url' | head -n 1)

version=${tag_download}
remove_prefix="v"
remove_suffix="-"
version=${version##*$remove_prefix}
version=${version%%$remove_suffix*}
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
