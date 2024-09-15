############################################################
# SteamCMD base on Ubuntu
# ref: 
#   https://developer.valvesoftware.com/wiki/SteamCMD#Ubuntu
#   https://github.com/CM2Walki/steamcmd/blob/master/bookworm/Dockerfile
############################################################

ARG base_image=ubuntu:latest
FROM ${base_image}

ARG USER=steam \
    PUID=1001 \
    LANGUAGE="en_US.UTF-8"

ENV USER=${USER} \
    PUID=${PUID} \
    DIR_USER="/home/${USER}" \
    LANGUAGE=${LANGUAGE} \
    LANG=${LANGUAGE} \
	LC_ALL=${LANGUAGE} \
    STEAMCMDDIR="/home/${USER}/steamcmd"

RUN set -x \
    # ===== Create unprivileged user =====
	&& useradd -u "${PUID}" -m "${USER}" \
    # ===== apt dependencies =====
	&& export DEBIAN_FRONTEND=noninteractive \
	&& apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
		ca-certificates \
		curl \
        lib32stdc++6 \
		lib32gcc-s1 \
        locales \
    # ===== System info =====
    && OS_ARCH=$(dpkg --print-architecture) \
    # ===== Setup Locale Encoding =====
	&& locale-gen ${LANGUAGE} \
	&& dpkg-reconfigure --frontend noninteractive locales \
    # ===== Setup steamcmd =====
    # ----- the multiverse repository and x86 packages must be enabled -----
    # && add-apt-repository multiverse \
    # && if [ "${OS_ARCH}" = "amd64" ]; then \
    #     dpkg --add-architecture i386; \
    # fi \
    # && apt-get update --ignore-missing -y -qq \
    # && echo steamcmd steam/question select "I AGREE" | debconf-set-selections \
    # && echo steamcmd steam/license note '' | debconf-set-selections \
    # && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
    #     steamcmd \
    # ----- dependencies required to run SteamCMD -----
    && mkdir -p ${STEAMCMDDIR} \
    && URL_steamcmd="https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" \
    && FILE_steamcmd="/tmp/steamcmd_linux.tar.gz" \
    && curl -fsSL ${URL_steamcmd} -o ${FILE_steamcmd} \
    # --strip-components=1: remove the first directory in the tarball
    && tar xzf ${FILE_steamcmd} -C ${STEAMCMDDIR} \
    && ls -lh ${STEAMCMDDIR} \
    && rm -f ${FILE_steamcmd} \
    # ===== Clean pre-install =====
    && apt-get purge --autoremove -y \
        curl \
    # ----- Download SteamCMD, execute as user -----
    # https://github.com/CM2Walki/steamcmd/blob/master/bookworm/Dockerfile
    # && mkdir -p "${STEAMCMDDIR}" \
    # && curl -fsSL 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz' | tar xvzf - -C "${STEAMCMDDIR}" \
    && "${STEAMCMDDIR}/steamcmd.sh" +quit \
    && ln -s "${STEAMCMDDIR}/linux32/steamclient.so" "${STEAMCMDDIR}/steamservice.so" \
    && mkdir -p "${HOMEDIR}/.steam/sdk32" \
    && ln -s "${STEAMCMDDIR}/linux32/steamclient.so" "${HOMEDIR}/.steam/sdk32/steamclient.so" \
    && ln -s "${STEAMCMDDIR}/linux32/steamcmd" "${STEAMCMDDIR}/linux32/steam" \
    && mkdir -p "${HOMEDIR}/.steam/sdk64" \
    && ln -s "${STEAMCMDDIR}/linux64/steamclient.so" "${HOMEDIR}/.steam/sdk64/steamclient.so" \
    && ln -s "${STEAMCMDDIR}/linux64/steamcmd" "${STEAMCMDDIR}/linux64/steam" \
    && ln -s "${STEAMCMDDIR}/steamcmd.sh" "${STEAMCMDDIR}/steam.sh" \
	# ----- Symlink steamclient.so; So misconfigured dedicated servers can find it -----
 	&& ln -s "${STEAMCMDDIR}/linux64/steamclient.so" "/usr/lib/x86_64-linux-gnu/steamclient.so" \
    # ----- Symlink steamcmd -----
    # && ln -s "${STEAMCMDDIR}/steamcmd.sh" "/usr/bin/steamcmd" \
    # ----- Clean /root/Steam/logs -----
    # && rm -rf /root/Steam/logs \
    # ===== Clean apt =====
    && apt-get autoremove -y -qq \
    && apt-get clean -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
	&& unset DEBIAN_FRONTEND \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env bash" >> ${sh_entrypoint} \
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

USER ${USER}

WORKDIR ${STEAMCMDDIR}

ENTRYPOINT ["/docker-entrypoint.sh"]
