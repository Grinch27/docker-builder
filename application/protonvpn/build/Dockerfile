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
    && gpg_file="/usr/share/keyrings/protonvpn_public.gpg" \
    && curl -fsSL https://repo.protonvpn.com/debian/public_key.asc | gpg --yes --dearmor --output ${gpg_file} \
    && echo "deb [signed-by=${gpg_file}] https://repo.protonvpn.com/debian stable main" > /etc/apt/sources.list.d/protonvpn.list \
    && apt-get update --ignore-missing -y -qq \
    # ===== get version =====
    && version=$(apt-cache madison protonvpn-stable-release | awk -F '|' '{print $2}' | tr -d ' ' | head -n 1) \
    # && echo "version=${version}" \
    # ===== Clean pre-install =====
    && apt-get autoremove --purge -y -qq \
        curl \
        gpg \
    # ===== Install protonvpn =====
    # && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
    #     proton-vpn-gnome-desktop \
    && URL_deb="https://repo.protonvpn.com/debian/dists/stable/main/binary-all/protonvpn-stable-release_${version}_all.deb" \
    && FILE_deb="/protonvpn-stable-release.deb" \
    && curl -fsSL ${URL_deb} -o ${FILE_deb} \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
        ${FILE_deb} \
    && rm -f ${FILE_deb} \
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
