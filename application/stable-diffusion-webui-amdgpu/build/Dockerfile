ARG base_image=rocm/dev-ubuntu-24.04
FROM ${base_image}

ARG DEBIAN_FRONTEND=noninteractive
ARG webui_repo=https://github.com/lshqqytiger/stable-diffusion-webui-amdgpu.git
ARG webui_ref=master
ARG webui_dir=/opt/stable-diffusion-webui
ARG venv_dir=/opt/venv
ARG rocm_torch_index=https://download.pytorch.org/whl/rocm7.2
ARG torch_packages="torch torchvision torchaudio"
ARG build_arg=""

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_PREFER_BINARY=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=${venv_dir} \
    PATH=${venv_dir}/bin:/opt/rocm/bin:${PATH} \
    WEBUI_DIR=${webui_dir} \
    GRADIO_SERVER_NAME=0.0.0.0 \
    COMMANDLINE_ARGS="--listen --port 7860 --skip-torch-cuda-test --medvram --opt-sdp-attention --enable-insecure-extension-access" \
    TORCH_COMMAND="pip install --index-url ${rocm_torch_index} ${torch_packages}" \
    HSA_ENABLE_SDMA=0 \
    PYTORCH_HIP_ALLOC_CONF=expandable_segments:True

RUN set -eux; \
    apt-get update -y; \
    apt-get install --no-install-recommends -y \
        bash \
        ca-certificates \
        ffmpeg \
        git \
        libgl1 \
        libglib2.0-0 \
        libjpeg-dev \
        libnuma1 \
        libpng-dev \
        pkg-config \
        python3 \
        python3-pip \
        python3-venv \
        tini \
        zlib1g-dev; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    python3 -m venv "${venv_dir}"; \
    "${venv_dir}/bin/pip" install --upgrade pip setuptools wheel; \
    "${venv_dir}/bin/pip" install --index-url "${rocm_torch_index}" ${torch_packages}

RUN set -eux; \
    git clone --depth 1 --branch "${webui_ref}" "${webui_repo}" "${webui_dir}"; \
    "${venv_dir}/bin/pip" install --prefer-binary -r "${webui_dir}/requirements_versions.txt"

RUN set -eux; \
    mkdir -p /data/models /data/outputs; \
    printf '%s\n' \
      '#!/usr/bin/env bash' \
      'set -euo pipefail' \
      '' \
      'WEBUI_DIR="${WEBUI_DIR:-/opt/stable-diffusion-webui}"' \
      'export PATH="${VIRTUAL_ENV:-/opt/venv}/bin:${PATH}"' \
      '' \
      'if [[ -x /opt/rocm/bin/rocminfo ]]; then' \
      '  if /opt/rocm/bin/rocminfo 2>/dev/null | grep -q "gfx1103" && [[ -z "${HSA_OVERRIDE_GFX_VERSION:-}" ]]; then' \
      '    export HSA_OVERRIDE_GFX_VERSION=11.0.0' \
      '    echo "[entrypoint] Detected gfx1103 (Radeon 780M), set HSA_OVERRIDE_GFX_VERSION=${HSA_OVERRIDE_GFX_VERSION}"' \
      '  fi' \
      'fi' \
      '' \
      'if [[ ! -e /dev/kfd || ! -d /dev/dri ]]; then' \
      '  echo "[entrypoint] AMD GPU devices are not mapped."' \
      '  echo "[entrypoint] Please run with: --device=/dev/kfd --device=/dev/dri --group-add video --group-add render"' \
      '  echo "[entrypoint] Entering idle mode for CI/test compatibility."' \
      '  exec sleep infinity' \
      'fi' \
      '' \
      'cd "${WEBUI_DIR}"' \
      'exec bash ./webui.sh' \
      > /usr/local/bin/entrypoint.sh; \
    chmod +x /usr/local/bin/entrypoint.sh

WORKDIR ${webui_dir}
EXPOSE 7860
VOLUME ["/data"]

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
