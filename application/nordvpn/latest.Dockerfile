ARG base_image=debian:stable-slim
FROM ${base_image}

RUN set -x \
    # ===== apt dependencies =====
	&& export DEBIAN_FRONTEND=noninteractive \
	&& apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
		ca-certificates \
		curl \
        gpg \
        # systemd \
        # sudo \
    # ===== Add nordvpn gpg key =====
    && curl -fsSL https://repo.nordvpn.com/gpg/nordvpn_public.asc | gpg --yes --dearmor --output /usr/share/keyrings/nordvpn_public.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/nordvpn_public.gpg] https://repo.nordvpn.com/deb/nordvpn/debian stable main" > /etc/apt/sources.list.d/nordvpn.list \
    && apt-get update --ignore-missing -y -qq \
    # ===== Clean pre-install =====
    && apt-get autoremove --purge -y -qq \
        curl \
        gpg \
        # sudo \
    # ===== Install nordvpn =====
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
        nordvpn \
    # ----- /etc/init.d/nordvpn -----
    && SOCKET_DIR=/run/nordvpn \
    && mkdir -m 0750 "$SOCKET_DIR" \
    && chown root:nordvpn "$SOCKET_DIR" \
    # && useradd -m user \
    # ===== Clean apt =====
    && apt-get autoremove --purge -y -qq \
    && apt-get clean -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
	&& unset DEBIAN_FRONTEND \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env bash" >> ${sh_entrypoint} \
    # ----- sh: /usr/sbin/nordvpnd -----
    && sh_nordvpn="/start-nordvpn.sh" \
	&& echo '/usr/sbin/nordvpnd' >> ${sh_nordvpn} \
    && echo '/usr/lib/nordvpn/norduserd' >> ${sh_nordvpn} \
	&& chmod +x ${sh_nordvpn} \
	&& echo "${sh_nordvpn} &" >> ${sh_entrypoint} \
    # ----- end of docker-entrypoint.sh -----
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

ENTRYPOINT ["/docker-entrypoint.sh"]

# # Plan B: Install deb
# && OS_ARCH=$(dpkg --print-architecture) \
# && echo "Detected architecture: ${OS_ARCH}" \
# && URL_DOWNLOAD='https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn_3.18.5' \
# && if [ "${OS_ARCH}" = "amd64" ]; then \
#     URL_DOWNLOAD="${URL_DOWNLOAD}_amd64.deb"; \
# elif [ "${OS_ARCH}" = "i386" ]; then \
#     URL_DOWNLOAD="${URL_DOWNLOAD}_i386.deb"; \
# elif [ "${OS_ARCH}" = "arm64" ]; then \
#     URL_DOWNLOAD="${URL_DOWNLOAD}_arm64.deb"; \
# elif [ "${OS_ARCH}" = "armhf" ]; then \
#     URL_DOWNLOAD="${URL_DOWNLOAD}_armhf.deb"; \
# else \
#     echo "Unsupported architecture: ${OS_ARCH}" && exit 1; \
# fi \
# && echo "Download URL: ${URL_DOWNLOAD}" \
# && export FILE_DEB="/nordvpn.deb" \
# && curl -fsSL ${URL_DOWNLOAD} -o ${FILE_DEB} \
# && apt-get install -y ${FILE_DEB} \
# && rm -f ${FILE_DEB} \
