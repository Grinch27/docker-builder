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
    # ===== Add protonvpn gpg key =====
    && curl -fsSL https://repo.protonvpn.com/debian/public_key.asc | gpg --yes --dearmor --output /usr/share/keyrings/protonvpn_public.gpg \
    && echo "deb https://repo.protonvpn.com/debian stable main" > /etc/apt/sources.list.d/protonvpn.list \
    && apt-get update --ignore-missing -y -qq \
    # ===== Clean pre-install =====
    && apt-get autoremove --purge -y -qq \
        curl \
        gpg \
    # ===== Install protonvpn =====
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
        protonvpn-stable-release \
    # ===== Clean apt =====
    && apt-get autoremove --purge -y -qq \
    && apt-get clean -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
	&& unset DEBIAN_FRONTEND \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env bash" >> ${sh_entrypoint} \
    # ----- sh: /bin/app -----
    # && sh_app="/start-app.sh" \
	# && echo '/bin/app' >> ${sh_app} \
	# && chmod +x ${sh_app} \
	# && echo "${sh_app} &" >> ${sh_entrypoint} \
    # ----- end of docker-entrypoint.sh -----
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

ENTRYPOINT ["/docker-entrypoint.sh"]
