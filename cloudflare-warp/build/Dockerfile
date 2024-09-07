ARG base_image=debian:stable-slim
FROM ${base_image}

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update --ignore-missing \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gpg \
        lsb-release \
    # ===== System info =====
    && OS_ARCH=$(dpkg --print-architecture) \
    && OS_VER=$(lsb_release -cs) \
    # ===== Add cloudflare gpg key =====
    && curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg \
    && echo "deb [arch=${OS_ARCH} signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ ${OS_VER} main" > /etc/apt/sources.list.d/cloudflare-client.list \
    # ===== Clean pre-install =====
    && apt-get purge --autoremove -y \
        curl \
        gpg \
        lsb-release \
    # ===== Install cloudflare-warp =====
    && apt-get update \
    && apt-get install -y \
        cloudflare-warp \
    # ===== Clean apt =====
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
    && unset DEBIAN_FRONTEND \
    # ===== docker-entrypoint.sh =====
    # && echo "#!/bin/sh\nservice dbus start\n/bin/warp-svc\nwarp-cli disconnect --accept-tos" > /docker-entrypoint.sh \
    && echo "#!/bin/sh\n/bin/warp-svc\nwarp-cli disconnect --accept-tos" > /docker-entrypoint.sh \
    && chmod +x /docker-entrypoint.sh
    
# ENTRYPOINT ["/bin/warp-svc"]
ENTRYPOINT ["/docker-entrypoint.sh"]
