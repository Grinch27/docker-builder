#!/bin/sh

set -eu

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

if [ -x /mnt/python/venv/bin/python ]; then
  py_cmd=/mnt/python/venv/bin/python
elif [ -x /opt/venv/bin/python ]; then
  py_cmd=/opt/venv/bin/python
else
  py_cmd=python3
fi

${py_cmd} --version || true

${py_cmd} - <<'PY'
try:
    import torch
    print(f"torch={torch.__version__}")
    print(f"hip={getattr(torch.version, 'hip', 'unknown')}")
    print(f"cuda_available={torch.cuda.is_available()}")
except Exception as exc:
    print(f"torch=unavailable ({exc})")
PY

if [ -f /etc/therock-version ]; then
  therock_version=$(awk 'NR==1 {print $1}' /etc/therock-version)
  echo "therock=${therock_version}"
fi

if [ -x /opt/rocm/bin/rocminfo ]; then
  /opt/rocm/bin/rocminfo >/dev/null 2>&1 || true
fi

if [ -d /app/.git ]; then
  commit_id=$(git -C /app rev-parse --short HEAD || true)
  echo "commit=${commit_id}"
fi

version=""
if [ -n "${ROCM_VERSION:-}" ]; then
  version="${ROCM_VERSION}"
elif [ -n "${THEROCK_VERSION:-}" ]; then
  version="${THEROCK_VERSION}"
elif [ -f /etc/therock-version ]; then
  version=$(awk 'NR==1 {print $1}' /etc/therock-version)
elif [ -f /opt/rocm/.info/version ]; then
  version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version)
elif [ -f /opt/rocm/.info/version-utils ]; then
  version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version-utils)
fi
version=$(echo "${version:-7.10}" | sed -E 's/^([0-9]+\.[0-9]+).*/\1/')

echo "version=rocm${version}"