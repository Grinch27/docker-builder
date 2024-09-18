############################################################
# base on Ubuntu
############################################################

ARG base_image=ubuntu:devel
FROM ${base_image}

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
        gcc-aarch64-linux-gnu \
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
        make \
        pngcrush \
        rsync \
        schedtool \
        squashfs-tools \
        vim \
        xsltproc \
        zip \
        zlib1g-dev \
        # ccache \
        # g++-multilib \
        # gcc-multilib \
    # ===== List upgradable =====
    && apt list --upgradable \
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

ENTRYPOINT ["/docker-entrypoint.sh"]
