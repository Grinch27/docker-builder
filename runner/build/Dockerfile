############################################################
# base on Ubuntu
############################################################

ARG base_image=ubuntu:latest
FROM ${base_image}

RUN set -x \
    # ===== apt dependencies =====
	&& export DEBIAN_FRONTEND=noninteractive \
    && packages_install=(
        "bc" 
        "bison" 
        "build-essential" 
        "ccache" 
        "curl" 
        "flex"
        "g++-multilib" 
        "gcc-multilib" 
        "git" 
        "git-lfs" 
        "gnupg"
        "gperf" 
        "imagemagick" 
        "lib32readline-dev" 
        "lib32z1-dev"
        "libelf-dev" 
        "liblz4-tool" 
        "libsdl1.2-dev" 
        "libssl-dev"
        "libxml2" 
        "libxml2-utils" 
        "lzop" 
        "pngcrush" 
        "rsync"
        "schedtool" 
        "squashfs-tools" 
        "xsltproc" 
        "zip" 
        "zlib1g-dev"
    ) \
	&& apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
		${packages_install[@]} \
    # ===== Clean apt =====
    && apt-get autoremove --purge -y -qq \
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

ENTRYPOINT ["/docker-entrypoint.sh"]
