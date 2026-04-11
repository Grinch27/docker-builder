#!/bin/sh

set -eu

VERSION="${1:?Error: VERSION is required}"
AMDGPU_FAMILY="${2:?Error: AMDGPU_FAMILY is required}"
RELEASE_TYPE="${3:-stable}"

VERSION_ENCODED=$(printf '%s' "${VERSION}" | sed 's/+/%2B/g')

case "${RELEASE_TYPE}" in
  stable)
    TARBALL_URL="https://repo.amd.com/rocm/tarball/therock-dist-linux-${AMDGPU_FAMILY}-${VERSION_ENCODED}.tar.gz"
    ;;
  nightlies|prereleases|devreleases)
    TARBALL_URL="https://rocm.${RELEASE_TYPE}.amd.com/tarball/therock-dist-linux-${AMDGPU_FAMILY}-${VERSION_ENCODED}.tar.gz"
    ;;
  *)
    echo "unsupported release type: ${RELEASE_TYPE}"
    exit 1
    ;;
esac

TARBALL_FILE=/tmp/therock-rocm.tar.gz
INSTALL_DIR="/opt/rocm-${VERSION}"

curl -fsSL -o "${TARBALL_FILE}" "${TARBALL_URL}"

rm -rf "${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
tar -xzf "${TARBALL_FILE}" -C "${INSTALL_DIR}"
rm -f "${TARBALL_FILE}"

ln -sfn "${INSTALL_DIR}" /opt/rocm

if [ ! -d "${INSTALL_DIR}/lib64" ] && [ -d "${INSTALL_DIR}/lib" ]; then
  ln -sfn lib "${INSTALL_DIR}/lib64"
fi

mkdir -p /opt/rocm/.info
printf '%s\n' "${VERSION}" > /opt/rocm/.info/version
printf '%s\n' "${VERSION}" > /opt/rocm/.info/version-utils
printf '/opt/rocm/lib\n/opt/rocm/lib64\n' > /etc/ld.so.conf.d/rocm.conf
ldconfig

for dir in bin include lib share; do
  if [ ! -d "${INSTALL_DIR}/${dir}" ]; then
    echo "missing ROCm directory: ${INSTALL_DIR}/${dir}"
    exit 1
  fi
done