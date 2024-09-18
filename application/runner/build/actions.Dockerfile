############################################################
# base on Ubuntu
############################################################

ARG base_image=ubuntu:devel
FROM ${base_image}

ARG dir_actions="/actions-runner"
RUN set -x \
    # ===== apt dependencies =====
	&& export DEBIAN_FRONTEND=noninteractive \
	&& apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
		bc \
        bison \
        build-essential \
        ca-certificates \
        curl \
        flex \
        g++-multilib \
        gcc-multilib \
        git \
        git-lfs \
        gnupg \
        gperf \
        imagemagick \
        lib32readline-dev \
        lib32z1-dev \
        libelf-dev \
        lz4 \
        libsdl1.2-dev \
        libssl-dev \
        libxml2 \
        libxml2-utils \
        lzop \
        pngcrush \
        rsync \
        schedtool \
        squashfs-tools \
        vim \
        xsltproc \
        zip \
        zlib1g-dev \
        # ccache \
        # sudo \
    # ----- List upgradable -----
    && apt list --upgradable \
    # ===== Setup runner =====
    # ----- Get latest version -----
    && version=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | grep 'tag_name' | cut -d ':' -f 2- | cut -d '"' -f 2) \
    && version=${version#v} \
    # ----- Create folder -----
    && mkdir -p ${dir_actions} \
    && cd ${dir_actions} \
    # ----- Download runner -----
    && OS_ARCH=$(dpkg --print-architecture) \
    && if [ "${OS_ARCH}" = "amd64" ]; then \
        URL_DOWNLOAD="https://github.com/actions/runner/releases/download/v${version}/actions-runner-linux-x64-${version}.tar.gz"; \
    elif [ "${OS_ARCH}" = "arm64" ]; then \
        URL_DOWNLOAD="https://github.com/actions/runner/releases/download/v${version}/actions-runner-linux-arm64-${version}.tar.gz"; \
    else \
        echo "Unsupported architecture: ${OS_ARCH}"; exit 1; \
    fi \
    && FILE_tar="/actions-runner.tar.gz" \
    && curl -fsSL ${URL_DOWNLOAD} -o ${FILE_tar} \
    # ----- Extract runner -----
    && tar xzf ${FILE_tar} -C ${dir_actions} \
    && rm -f ${FILE_tar} \
    # ===== Clean apt =====
    && apt-get autoremove --purge -y -qq \
    && apt-get clean -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
	&& unset DEBIAN_FRONTEND \
    # ===== fix /dev/shm =====
    && chmod +x /dev/shm \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env bash" >> ${sh_entrypoint} \
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

WORKDIR ${dir_actions}
# ENV RUNNER_ALLOW_RUNASROOT=true

ENTRYPOINT ["/docker-entrypoint.sh"]
