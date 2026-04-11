#!/bin/sh
set -eu

APP_DIR="${APP_DIR:-/app}"
SDNEXT_REPO="${SDNEXT_REPO:-https://github.com/vladmandic/sdnext.git}"
SDNEXT_REF="${SDNEXT_REF:-master}"
APP_DIR_FALLBACK="${APP_DIR_FALLBACK:-/tmp/sdnext-app}"

if [ ! -e /dev/kfd ] || [ ! -d /dev/dri ]; then
  echo "[entrypoint] AMD GPU devices are not mapped."
  echo "[entrypoint] Please run with: --device=/dev/kfd --device=/dev/dri --group-add video --group-add render"
  exec sleep infinity
fi

# In some deployments /app is bind-mounted and may not be writable.
if [ ! -d "${APP_DIR}" ]; then
  mkdir -p "${APP_DIR}" 2>/dev/null || true
fi

if [ ! -d "${APP_DIR}" ] || [ ! -w "${APP_DIR}" ]; then
  echo "[entrypoint] APP_DIR is not writable: ${APP_DIR}"
  APP_DIR="${APP_DIR_FALLBACK}"
  echo "[entrypoint] Fallback APP_DIR: ${APP_DIR}"
  mkdir -p "${APP_DIR}"
fi

if [ ! -d "${APP_DIR}/.git" ]; then
  git clone --depth 1 --branch "${SDNEXT_REF}" "${SDNEXT_REPO}" "${APP_DIR}"
fi

if [ -x /opt/rocm/bin/rocminfo ] && /opt/rocm/bin/rocminfo 2>/dev/null | grep -q "gfx1103" && [ -z "${HSA_OVERRIDE_GFX_VERSION:-}" ]; then
  export HSA_OVERRIDE_GFX_VERSION=11.0.0
fi

cd "${APP_DIR}"
exec ./webui.sh "$@"