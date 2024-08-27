ARG base_image=debian:stable-slim
FROM ${base_image}

ENV CODE="code" \
    SERVER="smart" \
    HEALTHCHECK="" \
    BEARER="" \
    NETWORK="on" \
    PROTOCOL="lightway_udp" \
    CIPHER="chacha20"

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update --ignore-missing \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        gpg \
        curl \
        lsb-release \
        systemd \
        # dbus \
        # nano \
        # man \
        expect \
        iproute2 \
        jq \
        # iptables \
        # nftables \
        iputils-ping \
        # vim \
        # sudo \
        # procps \
    # System info
    && OS_ARCH=$(dpkg --print-architecture) \
    && OS_VER=$(lsb_release -cs) \
    # Fix armhf
    && if [ "${OS_ARCH}" = "arm64" ]; then \
        dpkg --add-architecture armhf \
        && apt-get update --ignore-missing \
        && apt-get install -y --no-install-recommends --fix-missing \
            libc6:armhf \
            libstdc++6:armhf \
        && cd /lib \
        # && ln -s arm-linux-gnueabihf/ld-2.23.so ld-linux.so.3; \
        && ln -s $(find /lib -name 'ld-*.so' | grep 'arm-linux-gnueabihf' | head -n 1) ld-linux.so.3; \
    fi \
    # Download Expressvpn file
    && export URL_HTML="https://www.expressvpn.works/latest" \
    && export FILE_HTML="/latest.html" \
    && curl -fsSL ${URL_HTML} -o ${FILE_HTML} \
    && if [ "${OS_ARCH}" = "amd64" ]; then \
        URL_DOWNLOAD=$(grep -oP 'https://.*?/clients/linux/.*?_amd64.deb' ${FILE_HTML} | head -1); \
    elif [ "${OS_ARCH}" = "i386" ]; then \
        URL_DOWNLOAD=$(grep -oP 'https://.*?/clients/linux/.*?_i386.deb' ${FILE_HTML} | head -1); \
    elif echo "${OS_ARCH}" | grep -q "arm"; then \
        URL_DOWNLOAD=$(grep -oP 'https://.*?/clients/linux/.*?_armhf.deb' ${FILE_HTML} | head -1); \
    fi \
    && export FILE_DEB="/expressvpn.deb" \
    && curl -fsSL ${URL_DOWNLOAD} -o ${FILE_DEB} \
    && dpkg -i ${FILE_DEB} \
    && rm -f ${FILE_HTML} \
    && rm -f ${FILE_DEB} \
    # Clean pre-install
    && apt-get purge --autoremove -y \
        curl \
        lsb-release \
    # clear cache
    && apt clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
    && unset DEBIAN_FRONTEND

# ENTRYPOINT ["/startapp.sh"]
ENTRYPOINT ["sh", "-c", "uname -a && sleep infinity"]
