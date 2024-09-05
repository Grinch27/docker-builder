ARG base_image=debian:stable-slim
FROM ${base_image}

USER root

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update --ignore-missing \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gpg \
        # sudo \
    # Add nordvpn gpg key
    && curl -fsSL https://repo.nordvpn.com/gpg/nordvpn_public.asc | gpg --yes --dearmor --output /usr/share/keyrings/nordvpn_public.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/nordvpn_public.gpg] https://repo.nordvpn.com/deb/nordvpn/debian stable main" > /etc/apt/sources.list.d/nordvpn.list \
    && apt-get update \
    # Clean pre-install
    && apt-get purge --autoremove -y \
        curl \
        gpg \
    # Install nordvpn
    && apt-get install -y \
        nordvpn \
    # && useradd -m user \
    # # Uninstall sudo
    # && export SUDO_FORCE_REMOVE=yes \
    # && apt-get purge --autoremove -y \
    #     sudo \
    # && unset SUDO_FORCE_REMOVE \
    # Clean apt
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
    && unset DEBIAN_FRONTEND

# USER user
    
ENTRYPOINT ["sh", "-c", "uname -a && sleep infinity"]
