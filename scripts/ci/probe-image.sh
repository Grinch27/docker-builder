#!/bin/sh
# Central actual-version probe. Run inside the built image: sh probe-image.sh APP.
# Does not use Docker labels or the expected upstream version as a substitute.
set -eu
app="${1:-}"
case "$app" in
  aria2)
    version=$(aria2c --version | awk '/^aria2 version / {print $3; exit}')
    ;;
  curl)
    version=$(curl --version | awk 'NR==1 {print $2}')
    ;;
  privoxy)
    version=$(privoxy --version | awk '/Privoxy version / {print $3; exit}')
    ;;
  squid)
    version=$(squid --version | awk '/Squid Cache: Version/ {print $4; exit}')
    ;;
  dnscrypt-proxy)
    version=$(dnscrypt-proxy -version)
    ;;
  *)
    echo "Unsupported shared image probe: $app" >&2
    exit 2
    ;;
esac
if [ -z "$version" ]; then
  echo "Empty actual image version: $app" >&2
  exit 1
fi
case "$version" in
  *[![:print:]]*)
    echo "Invalid multiline image version: $app" >&2
    exit 1
    ;;
esac
printf "version=%s\n" "$version"
