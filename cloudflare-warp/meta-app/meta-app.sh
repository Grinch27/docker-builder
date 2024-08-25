#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

export DEBIAN_FRONTEND=noninteractive
apt-get update --ignore-missing
apt-get install -y --no-install-recommends -qq \
    ca-certificates \
    gpg \
    curl \
    lsb-release \
    systemd \
    # dbus \

# Add cloudflare gpg key
OS_ARCH=$(dpkg --print-architecture)
OS_VER=$(lsb_release -cs)
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
echo "deb [arch=${OS_ARCH} signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ ${OS_VER} main" > /etc/apt/sources.list.d/cloudflare-client.list

# Clean pre-install
apt-get purge --autoremove -y \
    curl \
    lsb-release

# Install cloudflare-warp
apt-get update
apt-get install -y \
    cloudflare-warp

# Clean apt
apt-get clean
rm -rf /var/lib/apt/lists/*
rm -rf /var/log/*.log
unset DEBIAN_FRONTEND

# ENTRYPOINT startapp.sh
echo "#!/bin/sh\nservice dbus start\n/bin/warp-svc\nwarp-cli disconnect --accept-tos" > /startapp.sh
chmod +x /startapp.sh

version=$(warp-cli --version)
remove_prefix="warp-cli "
version=${version##*$remove_prefix}
echo "version=${version}"
