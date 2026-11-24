# syntax=docker/dockerfile:1
# Bootstrap Valve's Linux client with 32-bit glibc, then run the amd64 client.
# Game-specific dependencies and Squad licensing remain deployment checks.
# Generate the locale SteamCMD requests and keep game data in a writable directory.
# Verify that both Steam SDK libraries exist after the client updates.

ARG base_image=debian:trixie-slim
FROM ${base_image}

ARG USER=steam
ARG PUID=1001

ENV HOME=/home/${USER} \
    USER=${USER} \
    PUID=${PUID} \
    LANG=en_US.UTF-8 \
    STEAMCMDDIR=/home/${USER}/steamcmd

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates curl lib32gcc-s1 lib32stdc++6 locales \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -f UTF-8 en_US.UTF-8 \
    && useradd --create-home --home-dir "$HOME" --uid "$PUID" --user-group "$USER" \
    && install -d -o "$USER" -g "$USER" "$STEAMCMDDIR" /data

COPY --chmod=0755 steamcmd /usr/bin/steamcmd

USER ${USER}
WORKDIR ${STEAMCMDDIR}

ARG STEAMCMD_MIRROR=
RUN set -eu; \
    installer_url=https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz; \
    set --; \
    if [ -n "$STEAMCMD_MIRROR" ]; then \
        mirror="${STEAMCMD_MIRROR%/}"; \
        installer_url="$mirror/steamcmd_linux.tar.gz"; \
        set -- -overridepackageurl "$mirror"; \
    fi; \
    curl -fsSL --retry 3 --connect-timeout 15 "$installer_url" -o steamcmd_linux.tar.gz; \
    tar -xzf steamcmd_linux.tar.gz; \
    rm steamcmd_linux.tar.gz; \
    steamcmd "$@" +quit; \
    test -x linux64/steamcmd \
    && test -s linux32/steamclient.so \
    && test -s linux64/steamclient.so \
    && mkdir -p "$HOME/.steam/sdk32" "$HOME/.steam/sdk64" \
    && ln -sf "$STEAMCMDDIR/linux32/steamclient.so" "$HOME/.steam/sdk32/steamclient.so" \
    && ln -sf "$STEAMCMDDIR/linux64/steamclient.so" "$HOME/.steam/sdk64/steamclient.so"

ENV STEAM_PLATFORM=linux64

ENTRYPOINT ["steamcmd"]
CMD ["+quit"]
