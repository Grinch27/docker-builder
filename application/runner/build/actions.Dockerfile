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
		ack \
        antlr3 \
        asciidoc \
        autoconf \
        automake \
        autopoint \
        binutils \
        bison \
        build-essential \
        bzip2 \
        clang \
        clangd \
        cmake \
        cpio \
        curl \
        device-tree-compiler \
        dwarves \
        ecj \
        fastjar \
        flex \
        gawk \
        g++ \
        gcc \
        gcc-aarch64-linux-gnu \
        git \
        gperf \
        haveged \
        help2man \
        intltool \
        jq \
        libelf-dev \
        libglib2.0-dev \
        libgmp3-dev \
        libltdl-dev \
        libmpc-dev \
        libmpfr-dev \
        libncurses5-dev \
        libreadline-dev \
        libssl-dev \
        libtool \
        lld \
        lldb \
        make \
        mkisofs \
        ninja-build \
        p7zip-full \
        patch \
        pkgconf \
        python3 \
        python3-pip \
        re2c \
        rsync \
        scons \
        squashfs-tools \
        subversion \
        swig \
        uglifyjs \
        unzip \
        vim \
        wget \
        zlib1g-dev \
        \
        bc \
        ca-certificates \
        git-lfs \
        gnupg \
        lz4 \
        libxml2 \
        libxml2-utils \
        lzop \
        schedtool \
        xsltproc \
        zip \
        # ----- abort -----
        # imagemagick \
        # lib32readline-dev \
        # lib32z1-dev \
        # libsdl1.2-dev \
        # pngcrush \
        # "ccache"
        # "lib32gcc-s1"
        # "libc6-dev-i386"
        # "libdb++-dev"
        # "gcc-multilib"
        # "g++-multilib"
        # "libncursesw5"
        # "libncursesw5-dev"
        # "lrzsz"
        # "msmtp"
        # "nano"
        # "p7zip"
        # "python3-docutils"
        # "python3-ply"
        # "qemu-utils"
        # "texinfo"
        # "xmlto"
        # "xxd"
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
ENV RUNNER_ALLOW_RUNASROOT=true

ENTRYPOINT ["/docker-entrypoint.sh"]
