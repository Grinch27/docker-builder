ARG base_image=debian:stable-slim
FROM ${base_image}

# ENV CODE="code" \
#     SERVER="smart" \
#     HEALTHCHECK="" \
#     BEARER="" \
#     NETWORK="on" \
#     PROTOCOL="lightway_udp" \
#     CIPHER="chacha20"

RUN set -x \
    # ===== apt dependencies =====
	&& export DEBIAN_FRONTEND=noninteractive \
	&& apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
		ca-certificates \
		curl \
        gpg \
        lsb-release \
    # ===== System info =====
    && OS_ARCH=$(dpkg --print-architecture) \
    && OS_VER=$(lsb_release -cs) \
    # ===== Fix armhf =====
    && if [ "${OS_ARCH}" = "arm64" ]; then \
        dpkg --add-architecture armhf \
        && apt-get update --ignore-missing -y -qq \
        && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
            libc6:armhf \
            libstdc++6:armhf \
        && cd /lib \
        # && ln -s arm-linux-gnueabihf/ld-2.23.so ld-linux.so.3; \
        && ln -s $(find /lib -name 'ld-*.so' | grep 'arm-linux-gnueabihf' | head -n 1) ld-linux.so.3; \
    fi \
    # ===== Download Expressvpn =====
    && URL_HTML="https://www.expressvpn.works/latest" \
    && FILE_HTML="/latest.html" \
    && curl -fsSL ${URL_HTML} -o ${FILE_HTML} \
    && if [ "${OS_ARCH}" = "amd64" ]; then \
        URL_DOWNLOAD=$(grep -oP 'https://.*?/clients/linux/.*?_amd64.deb' ${FILE_HTML} | head -1); \
    elif [ "${OS_ARCH}" = "i386" ]; then \
        URL_DOWNLOAD=$(grep -oP 'https://.*?/clients/linux/.*?_i386.deb' ${FILE_HTML} | head -1); \
    elif echo "${OS_ARCH}" | grep -q "arm"; then \
        URL_DOWNLOAD=$(grep -oP 'https://.*?/clients/linux/.*?_armhf.deb' ${FILE_HTML} | head -1); \
    fi \
    && FILE_DEB="/expressvpn.deb" \
    && curl -fsSL ${URL_DOWNLOAD} -o ${FILE_DEB} \
    # ===== Clean pre-install =====
    && apt-get autoremove --purge -y -qq \
        curl \
        gpg \
        lsb-release \
    # ===== Install expressvpn =====
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
        ${FILE_DEB} \
    && rm -f ${FILE_HTML} \
    && rm -f ${FILE_DEB} \
    # ===== Clean apt =====
    && apt-get autoremove --purge -y -qq \
    && apt-get clean -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
	&& unset DEBIAN_FRONTEND \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env bash" >> ${sh_entrypoint} \
    # ----- sh: /usr/sbin/expressvpnd -----
    && sh_expressvpnd="/start-expressvpnd.sh" \
	&& echo '/etc/init.d/expressvpn start' >> ${sh_expressvpnd} \
	&& chmod +x ${sh_expressvpnd} \
	&& echo "${sh_expressvpnd} &" >> ${sh_entrypoint} \
    # ----- end of docker-entrypoint.sh -----
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

ENTRYPOINT ["/docker-entrypoint.sh"]
