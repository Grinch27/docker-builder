#==============================
# Inpired by:
#	https://github.com/jlesage/docker-baseimage-gui
#	https://github.com/SeleniumHQ/docker-selenium
#==============================

# ===== Build: noVNC =====
ARG base_image=debian:stable-slim
FROM ${base_image} AS novnc
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



# ===== Build: /var/lib/openbox/debian-menu.xml =====
ARG base_image=debian:stable-slim
FROM ${base_image} AS menu
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --fix-missing -y -qq \
		openbox \
		obconf \
        menu \
		python3-pyxdg \
	# ----- menu generate -----
    && update-menus



# ===== Build: /usr/bin/xset =====
ARG base_image=debian:stable-slim
FROM ${base_image} AS xset
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --fix-missing -y -qq \
		x11-xserver-utils



# ===== Main =====
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

ARG PATH_noVNC="/opt/bin/noVNC"
COPY --from=novnc ${PATH_noVNC} ${PATH_noVNC}
COPY --from=menu /var/lib/openbox/debian-menu.xml /var/lib/openbox/debian-menu.xml
COPY --from=xset /usr/bin/xset /usr/bin/xset
RUN export DEBIAN_FRONTEND=noninteractive \
	# ===== non-apt Install =====
	&& apt-get update --ignore-missing -y -qq \
	&& apt-get install --no-install-recommends --fix-missing -y -qq \
		ca-certificates \
		curl \
		gpg \
	# ===== System info =====
    && OS_ARCH=$(dpkg --print-architecture) \
	# ===== baidunetdisk: Pre-Setup =====
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
		# x11-xserver-utils \
		# ----- Fluxbox -----
		# fluxbox \
		# eterm \
		# hsetroot \
		# feh \
		# ----- Openbox -----
		openbox \
		# obconf \
		# menu \
		python3-pyxdg \
		# lxappearance \
		# tint2 \
		# xcompmgr \
		# ----- Locale Encoding -----
		# language-pack-zh-hans \
		# locales \
		# libfontconfig \
		# libfreetype6 \
		# xfonts-scalable \
		# xfonts-cyrillic \
		# fonts-ubuntu \
		# fonts-liberation \
		# fonts-ipafont-gothic \
		fonts-wqy-zenhei \
		# fonts-tlwg-loma-otf \
		# fonts-noto-color-emoji \
	# ===== Setup Locale Encoding =====
	# && locale-gen ${LANGUAGE} \
	# && dpkg-reconfigure --frontend noninteractive locales \
	# ===== noVNC =====
	&& ln -s "${PATH_noVNC}/utils/novnc_proxy" /usr/local/bin/novnc \
	# ===== baidunetdisk =====
	&& apt-get install --no-install-recommends --fix-missing -y -qq \
		${FILE_baidunetdisk} \
		# ----- Misc -----
		libasound2 \
		libgbm1 \
		libgtk-3-0 \
		libnss3 \
		# libxss1 \
		desktop-file-utils \
		# libnotify4 \
		xdg-utils \
		libsecret-common \
		libsecret-1-0 \
		libdbusmenu-glib4 \
		libdbusmenu-gtk3-4 \
		# libappindicator3-1 \
		libxtst6 \
		libx11-xcb1 \
		# ttf-wqy-zenhei \
		# procps \
		bzip2 \
    && rm -f ${FILE_baidunetdisk} \
	&& PATH_baidunetdisk="/opt/baidunetdisk" \
	&& ln -s "${PATH_baidunetdisk}/baidunetdisk" /usr/local/bin/baidunetdisk \
	# -----clean baidunetdisk -----
    && tar -cjvf ${PATH_baidunetdisk}/LICENSES.chromium.html.tar.bz2 -C ${PATH_baidunetdisk} LICENSES.chromium.html \
    && rm ${PATH_baidunetdisk}/LICENSES.chromium.html \
	&& apt-get purge --autoremove -y -qq \
        bzip2 \
	&& rm -rf ${PATH_baidunetdisk}/resources/app.asar.unpacked/node_modules/@baidu/clipboard-listen-macos/src \
	&& for file in /opt/baidunetdisk/locales/*.pak; do \
        case $(basename "${file}") in \
            en-GB.pak|en-US.pak|zh-CN.pak|zh-TW.pak) ;; \
            *) rm -f "${file}"; echo "Deleting ${file}";; \
        esac; \
    done \
	# ===== Misc =====
	# ----- fix executable file permissions of /dev/shm for Docker Desktop and WSL2 -----
	&& chmod +x /dev/shm \
	# ----- Setup Xvfb directory -----
	&& mkdir -p /tmp/.X11-unix \
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
	# ----- sh: start Xvfb & Openbox -----
	&& sh_xvfb="/start-xvfb.sh" \
	&& echo 'rm -f /tmp/.X*lock' >> ${sh_xvfb} \
	&& echo 'xvfb-run --server-num=${DISPLAY_NUM} --server-args="-screen 0 ${SCREEN_WIDTH}x${SCREEN_HEIGHT}x${SCREEN_DEPTH} -fbdir /var/tmp -dpi ${SCREEN_DPI} -listen tcp -noreset -ac +extension RANDR" openbox-session' >> ${sh_xvfb} \
	&& chmod +x ${sh_xvfb} \
	&& echo "${sh_xvfb} &" >> /docker-entrypoint.sh \
	# ----- start vnc -----
	&& sh_x11vnc="/start-x11vnc.sh" \
	&& echo 'for i in $(seq 1 10); do { sleep 1; xdpyinfo -display ${DISPLAY} && break || echo "Wait for Xvfb"; }; done' >> ${sh_x11vnc} \
	&& echo 'x11vnc -forever -shared -rfbport ${VNC_PORT} -display ${DISPLAY}' >> ${sh_x11vnc} \
	&& chmod +x ${sh_x11vnc} \
	&& echo "${sh_x11vnc} &" >> /docker-entrypoint.sh \
	# ----- start novnc -----
	&& sh_novnc="/start-novnc.sh" \
	&& echo 'novnc --listen ${NO_VNC_PORT} --vnc localhost:${VNC_PORT}' >> ${sh_novnc} \
	&& chmod +x ${sh_novnc} \
	&& echo "${sh_novnc} &" >> /docker-entrypoint.sh \
	# ----- start app -----
	&& sh_app="/start-app.sh" \
	&& echo "baidunetdisk --disable-gpu-sandbox --no-sandbox" >> ${sh_app} \
	&& chmod +x ${sh_app} \
	&& echo "${sh_app} &" >> /docker-entrypoint.sh \
	# ----- sleep infinity -----
	&& echo "uname -a\nsleep infinity" >> /docker-entrypoint.sh \
	&& chmod +x /docker-entrypoint.sh

EXPOSE 5900 7900

ENTRYPOINT ["sh", "/docker-entrypoint.sh"]