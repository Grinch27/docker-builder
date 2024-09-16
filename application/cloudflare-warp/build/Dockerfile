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
        lsb-release \
    # ===== System info =====
    && OS_ARCH=$(dpkg --print-architecture) \
    && OS_VER=$(lsb_release -cs) \
    # ===== Add cloudflare gpg key =====
    && curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg \
    && echo "deb [arch=${OS_ARCH} signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ ${OS_VER} main" > /etc/apt/sources.list.d/cloudflare-client.list \
    && apt-get update \
    # ===== Clean pre-install =====
    && apt-get autoremove --purge -y -qq \
        curl \
        gpg \
        lsb-release \
    # ===== Install cloudflare-warp =====
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
        cloudflare-warp \
    # ===== Clean apt =====
    && apt-get autoremove --purge -y -qq \
    && apt-get clean -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
	&& unset DEBIAN_FRONTEND \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env bash" >> ${sh_entrypoint} \
    # ----- sh: /bin/warp-svc -----
    && sh_warp="/start-warp.sh" \
	&& echo '/bin/warp-svc' >> ${sh_warp} \
    && echo 'warp-cli disconnect --accept-tos' >> ${sh_warp} \
	&& chmod +x ${sh_warp} \
	&& echo "${sh_warp} &" >> ${sh_entrypoint} \
    # ----- end of docker-entrypoint.sh -----
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}
    
# ENTRYPOINT ["/bin/warp-svc"]
ENTRYPOINT ["/docker-entrypoint.sh"]
