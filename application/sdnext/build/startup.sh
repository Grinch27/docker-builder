#!/bin/sh
set -eu

APP_DIR="${APP_DIR:-/app}"
SDNEXT_REPO="${SDNEXT_REPO:-https://github.com/vladmandic/sdnext.git}"
SDNEXT_REF="${SDNEXT_REF:-master}"

if [ ! -d "${APP_DIR}/.git" ]; then
  git clone --depth 1 --branch "${SDNEXT_REF}" "${SDNEXT_REPO}" "${APP_DIR}"
fi

if [ -x /opt/rocm/bin/rocminfo ] && /opt/rocm/bin/rocminfo 2>/dev/null | grep -q "gfx1103" && [ -z "${HSA_OVERRIDE_GFX_VERSION:-}" ]; then
  export HSA_OVERRIDE_GFX_VERSION=11.0.0
fi

if [ ! -e /dev/kfd ] || [ ! -d /dev/dri ]; then
  echo "[entrypoint] AMD GPU devices are not mapped."
  echo "[entrypoint] Please run with: --device=/dev/kfd --device=/dev/dri --group-add video --group-add render"
  exec sleep infinity
fi

cd "${APP_DIR}"
exec ./webui.sh "$@"
