#!/bin/sh
# Install Valve HLDS App 90 from the public branch with the cstrike mod.
# Recheck the required game files if Valve changes the Linux depot layout.
# Reuse installed files and retry incomplete first downloads in the same volume.
# Reject incomplete installs and competing uses of the same server data.
set -eu

server_files_ready() {
  test -x ./hlds_linux &&
    test -s ./valve/liblist.gam &&
    test -s ./cstrike/liblist.gam &&
    test -s ./cstrike/dlls/cs.so &&
    test -s ./cstrike/maps/de_dust2.bsp
}

install_server() {
  for attempt in 1 2 3; do
    if steamcmd +@ShutdownOnFailedCommand 1 +force_install_dir "$PWD" +login anonymous \
      +app_set_config 90 mod cstrike +app_update 90 validate +quit &&
      server_files_ready; then
      return 0
    fi
    printf 'HLDS download incomplete after attempt %s of 3\n' "$attempt" >&2
  done
  return 1
}

exec 9>.cs16.lock
if ! flock -n 9; then
  echo 'This CS 1.6 data directory is already in use' >&2
  exit 1
fi

if [ -e .cs16-installing ] || ! server_files_ready; then
  touch .cs16-installing
  install_server
  rm .cs16-installing
fi

export SteamAppId=10
export LD_LIBRARY_PATH="$PWD${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec ./hlds_linux -game cstrike -console "$@"
