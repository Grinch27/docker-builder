ARG base_image=debian:stable-slim
FROM ${base_image} AS noVNC
ARG PATH_noVNC="/opt/bin/noVNC"
RUN export DEBIAN_FRONTEND=noninteractive \
	# ===== non-apt Install =====
	&& apt-get update --ignore-missing -y -qq \
	&& apt-get install --no-install-recommends --fix-missing -y -qq \
		ca-certificates \
		curl \
		gpg \
	# ===== noVNC =====
	&& URL_noVNC=$(curl -s https://api.github.com/repos/novnc/noVNC/releases/latest | grep 'tarball_url' | cut -d ':' -f 2- | cut -d '"' -f 2) \
    && FILE_noVNC="/noVNC-latest.tar.gz" \
	# && PATH_noVNC="/opt/bin/noVNC" \
	# ----- noVNC: Setup -----
	&& curl -fsSL ${URL_noVNC} -o ${FILE_noVNC} \
	&& mkdir -p ${PATH_noVNC} \
    && tar xzf ${FILE_noVNC} -C ${PATH_noVNC} --strip-components=1 \
    && cp "${PATH_noVNC}/vnc.html" "${PATH_noVNC}/index.html" \
    && rm -f ${FILE_noVNC} \
	# ----- noVNC: Clean -----
	&& rm -rf "${PATH_noVNC}/.github" \
	&& rm -rf "${PATH_noVNC}/docs" \
	&& rm -rf "${PATH_noVNC}/snap" \
	&& rm -rf "${PATH_noVNC}/tests" \
	# ===== websockify =====
	&& URL_websockify=$(curl -s https://api.github.com/repos/novnc/websockify/releases/latest | grep 'tarball_url' | cut -d ':' -f 2- | cut -d '"' -f 2) \
    && FILE_websockify="/websockify.tar.gz" \
	&& PATH_websockify="${PATH_noVNC}/utils/websockify" \
	# ----- websockify: Setup -----
	&& curl -fsSL ${URL_websockify} -o ${FILE_websockify} \
	&& mkdir -p ${PATH_websockify} \
    && tar xzf ${FILE_websockify} -C ${PATH_websockify} --strip-components=1 \
	&& rm -f ${FILE_websockify} \
	# ----- websockify: Clean -----
	&& rm -rf "${PATH_websockify}/.github" \
	&& rm -rf "${PATH_websockify}/docker" \
	&& rm -rf "${PATH_websockify}/docs" \
	&& rm -rf "${PATH_websockify}/tests"



ARG base_image=debian:stable-slim
FROM ${base_image}

ARG LANGUAGE=C
ENV	LANGUAGE=${LANGUAGE} \
    LANG=${LANGUAGE} \
	LC_ALL=${LANGUAGE} \
	# ----- xvfb -----
	SCREEN_WIDTH=1920 \
    SCREEN_HEIGHT=1080 \
    SCREEN_DEPTH=24 \
    SCREEN_DPI=96 \
	# ----- VNC -----
	VNC_PORT=5900 \
	NO_VNC_PORT=7900 \
	DISPLAY=:99.0 \
    DISPLAY_NUM=99

# --mount=type=secret,id=NOVNC_PASSWD
ARG PATH_noVNC="/opt/bin/noVNC"
COPY --from=noVNC ${PATH_noVNC} ${PATH_noVNC}
RUN export DEBIAN_FRONTEND=noninteractive \
	# ===== non-apt Install =====
	&& apt-get update --ignore-missing -y -qq \
	&& apt-get install --no-install-recommends --fix-missing -y -qq \
		ca-certificates \
		curl \
		gpg \
	# ===== System info =====
    && OS_ARCH=$(dpkg --print-architecture) \
	# ===== baidunetdisk =====
	# ----- baidunetdisk: Pre-Setup -----
	&& APP_VER="4.17.7" \
	&& URL_baidunetdisk="https://pkg-ant.baidu.com/issue/netdisk/LinuxGuanjia/${APP_VER}/baidunetdisk_${APP_VER}_${OS_ARCH}.deb" \
	&& FILE_baidunetdisk="/baidunetdisk.deb" \
	&& curl -fsSL ${URL_baidunetdisk} -o ${FILE_baidunetdisk} \
	# ===== Clean pre-install =====
    && apt-get purge --autoremove -y -qq \
        curl \
        gpg \
	# ===== main Install =====
	&& apt-get update --ignore-missing -y -qq \
	&& apt-get install --no-install-recommends --fix-missing -y -qq \
		# ----- Xvfb -----
		xvfb \
		libxcb1 \
		xauth \
		# pulseaudio \
		# ----- VNC -----
		x11vnc	\
		x11-utils \
		# # ----- Fluxbox -----
		# fluxbox \
		eterm \
		hsetroot \
		feh \
		# ----- Openbox -----
		openbox \
		obconf \
		menu \
		lxappearance \
		tint2 \
		xcompmgr \
		# ----- Locale Encoding -----
		# language-pack-zh-hans \
		locales \
		libfontconfig \
		libfreetype6 \
		xfonts-scalable \
		# xfonts-cyrillic \
		# fonts-ubuntu \
		# fonts-liberation \
		# fonts-ipafont-gothic \
		fonts-wqy-zenhei \
		# fonts-tlwg-loma-otf \
		# fonts-noto-color-emoji \
	# ===== Setup Locale Encoding =====
	&& locale-gen ${LANGUAGE} \
	&& dpkg-reconfigure --frontend noninteractive locales \
	# ===== openbox =====
	&& apt-get install --no-install-recommends --fix-missing -y -qq \
        python3-pyxdg \
	# ===== noVNC =====
	&& ln -s "${PATH_noVNC}/utils/novnc_proxy" /usr/local/bin/novnc \
	# ===== baidunetdisk =====
	&& apt-get install --no-install-recommends --fix-missing -y -qq ${FILE_baidunetdisk} \
    && rm -f ${FILE_baidunetdisk} \
	# ===== fix executable file permissions of /dev/shm for Docker Desktop and WSL2 =====
	&& chmod +x /dev/shm \
	# ===== Creating Xvfb base directory =====
	&& mkdir -p /tmp/.X11-unix \
	# ----- Generating VNC password -----
	# && x11vnc -storepasswd $(cat /run/secrets/NOVNC_PASSWD) ${HOME}/.vnc/passwd \
	&& chmod -R 775 ${HOME} /tmp/.X11-unix \
	&& chgrp -R 0 ${HOME} /tmp/.X11-unix \
	&& chmod -R g=u ${HOME} /tmp/.X11-unix \
	# ===== Clean apt =====
	&& apt-get autoremove -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
    && apt-get clean -y -qq \
	&& unset DEBIAN_FRONTEND \
	# ===== docker-entrypoint.sh =====
    && echo "#!/usr/bin/env sh" >> /docker-entrypoint.sh \
	# code reference: https://github.com/SeleniumHQ/docker-selenium/
	# # ----- start Xvfb & Fluxbox -----
	# && echo 'rm -f /tmp/.X*lock' >> /docker-entrypoint.sh \
	# && echo '/usr/bin/xvfb-run --server-num=${DISPLAY_NUM} --server-args="-screen 0 ${SCREEN_WIDTH}x${SCREEN_HEIGHT}x${SCREEN_DEPTH} -fbdir /var/tmp -dpi ${SCREEN_DPI} -listen tcp -noreset -ac +extension RANDR" /usr/bin/fluxbox -display ${DISPLAY}' >> /docker-entrypoint.sh \
	# ----- start Xvfb & Openbox -----
	&& echo 'rm -f /tmp/.X*lock' >> /docker-entrypoint.sh \
	&& echo 'xvfb-run --server-num=${DISPLAY_NUM} --server-args="-screen 0 ${SCREEN_WIDTH}x${SCREEN_HEIGHT}x${SCREEN_DEPTH} -fbdir /var/tmp -dpi ${SCREEN_DPI} -listen tcp -noreset -ac +extension RANDR" openbox-session' >> /docker-entrypoint.sh \
	# ----- start vnc -----
	# x11vnc -storepasswd ${VNC_PASSWORD} ${HOME}/.vnc/passwd
	# no -usepw (without password), no -viewonly
	&& echo 'for i in $(seq 1 10); do sleep 1 && xdpyinfo -display ${DISPLAY} >/dev/null 2>&1 && break || echo "Wait for Xvfb Starting"; done' >> /docker-entrypoint.sh \
	&& echo 'x11vnc -forever -shared -rfbport ${VNC_PORT} -display ${DISPLAY}' >> /docker-entrypoint.sh \
	# ----- start novnc -----
	&& echo '/opt/bin/noVNC/utils/novnc_proxy --listen ${NO_VNC_PORT} --vnc localhost:${VNC_PORT}' >> /docker-entrypoint.sh \
	# ----- sleep infinity -----
	&& echo "uname -a\nsleep infinity" >> /docker-entrypoint.sh \
	&& chmod +x /docker-entrypoint.sh

# ===== Suggest Run as non-privileged user =====
# USER root

# 暴露 noVNC 和 VNC 端口
EXPOSE 5900 7900

ENTRYPOINT ["sh", "/docker-entrypoint.sh"]