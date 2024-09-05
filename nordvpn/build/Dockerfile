ARG base_image=debian:stable-slim
FROM ${base_image}

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update --ignore-missing \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gpg \
        systemd \
        # sudo \
    # Add nordvpn gpg key
    # && curl -fsSL https://repo.nordvpn.com/gpg/nordvpn_public.asc | gpg --yes --dearmor --output /usr/share/keyrings/nordvpn_public.gpg \
    # && echo "deb [signed-by=/usr/share/keyrings/nordvpn_public.gpg] https://repo.nordvpn.com/deb/nordvpn/debian stable main" > /etc/apt/sources.list.d/nordvpn.list \
    # && apt-get update \
    # Plan B: Install deb
    && OS_ARCH=$(dpkg --print-architecture) \
    && if [ "${OS_ARCH}" = "amd64" ]; then \
        URL_DOWNLOAD=$(grep -oP 'https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn_3.18.5_amd64.deb' ${FILE_HTML} | head -1); \
    elif [ "${OS_ARCH}" = "i386" ]; then \
        URL_DOWNLOAD=$(grep -oP 'https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn_3.18.5_i386.deb' ${FILE_HTML} | head -1); \
    elif [ "${OS_ARCH}" = "arm64" ]; then \
        URL_DOWNLOAD=$(grep -oP 'https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn_3.18.5_arm64.deb' ${FILE_HTML} | head -1); \
    elif [ "${OS_ARCH}" = "armhf" ]; then \
        URL_DOWNLOAD=$(grep -oP 'https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn_3.18.5_armhf.deb' ${FILE_HTML} | head -1); \
    fi \
    && export FILE_DEB="/nordvpn.deb" \
    && curl -fsSL ${URL_DOWNLOAD} -o ${FILE_DEB} \
    && dpkg -i ${FILE_DEB} \
    && rm -f ${FILE_DEB} \
    # Clean pre-install
    && apt-get purge --autoremove -y \
        curl \
        gpg \
    # Install nordvpn
    # && apt-get install -y \
    #     nordvpn \
    # Clean apt
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
    && unset DEBIAN_FRONTEND
    
# ENTRYPOINT ["sh", "-c", "uname -a && sleep infinity"]
# systemctl enable --now nordvpnd
ENTRYPOINT ["systemctl enable --now nordvpnd"]
