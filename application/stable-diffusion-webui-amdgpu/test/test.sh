#!/bin/sh

set -eu

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

if [ -x /opt/venv/bin/python ]; then
	py_cmd=/opt/venv/bin/python
else
	py_cmd=python3
fi

${py_cmd} --version

${py_cmd} - <<'PY'
import torch
print(f"torch={torch.__version__}")
print(f"hip={getattr(torch.version, 'hip', 'unknown')}")
print(f"cuda_available={torch.cuda.is_available()}")
PY

if [ -x /opt/rocm/bin/rocminfo ]; then
	/opt/rocm/bin/rocminfo >/dev/null 2>&1 || true
fi

if [ -d /opt/stable-diffusion-webui/.git ]; then
	commit_id=$(git -C /opt/stable-diffusion-webui rev-parse --short HEAD)
	echo "commit=${commit_id}"
fi

version=$(${py_cmd} - <<'PY'
import torch
hip = getattr(torch.version, "hip", "unknown")
if isinstance(hip, str) and hip and hip != "unknown":
		parts = hip.split(".")
		hip = ".".join(parts[:2])
print(f"rocm{hip}-torch{torch.__version__}")
PY
)

echo "version=${version}"
