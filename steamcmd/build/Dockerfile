ARG base_image=ubuntu:latest
FROM ${base_image}

ARG PUID=1001 \
    USER=steam

ENV USER=steam \
    HOMEDIR="/home/${USER}"
    # STEAMCMDDIR="/home/${USER}/steamcmd"

RUN set -x \
	&& export DEBIAN_FRONTEND=noninteractive \
	&& apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
		ca-certificates \
		# curl \
        lib32stdc++6 \
		lib32gcc-s1 \
    # ===== System info =====
    && OS_ARCH=$(dpkg --print-architecture) \
    # install SteamCMD the multiverse repository and x86 packages must be enabled
    # && add-apt-repository multiverse \
    && if [ "${OS_ARCH}" = "amd64" ]; then \
        dpkg --add-architecture i386; \
    fi \
    && apt-get update --ignore-missing -y -qq \
    && echo steamcmd steam/question select "I AGREE" | debconf-set-selections \
    && echo steamcmd steam/license note '' | debconf-set-selections \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
        steamcmd \
	# Create unprivileged user
	&& useradd -u "${PUID}" -m "${USER}" \
	# ===== Clean apt =====
    && apt-get autoremove -y -qq \
    && apt-get clean -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
	&& unset DEBIAN_FRONTEND \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

USER ${USER}

# WORKDIR ${STEAMCMDDIR}

ENTRYPOINT ["sh", "/docker-entrypoint.sh"]