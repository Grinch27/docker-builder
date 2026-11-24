# syntax=docker/dockerfile:1
# Run the official public HLDS Linux build with the cstrike mod.
# Check the current SteamCMD base and 32-bit runtime when updating HLDS.
# Install the game on first start and reuse the data volume on later starts.
# Verify startup and game query responses throughout the acceptance window.

ARG base_image=steamcmd:dev
FROM ${base_image}

COPY --chmod=0755 entrypoint.sh /usr/local/bin/cs16-server
WORKDIR /data

EXPOSE 27015/udp
ENTRYPOINT ["/usr/local/bin/cs16-server"]
CMD ["-port", "27015", "+maxplayers", "16", "+map", "de_dust2"]
