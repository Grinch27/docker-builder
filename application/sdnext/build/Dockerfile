ARG base_image=rocm/dev-ubuntu-24.04
FROM ${base_image}

ARG DEBIAN_FRONTEND=noninteractive
ARG sdnext_repo=https://github.com/vladmandic/sdnext.git
ARG sdnext_ref=master
ARG app_dir=/app
ARG rocm_torch_index=https://download.pytorch.org/whl/rocm7.2
ARG torch_packages="torch torchvision torchaudio"
ARG build_arg=""

LABEL org.opencontainers.image.vendor="SD.Next" \
      org.opencontainers.image.authors="docker-builder" \
      org.opencontainers.image.url="https://github.com/vladmandic/sdnext/" \
      org.opencontainers.image.documentation="https://github.com/vladmandic/sdnext/wiki/Docker" \
      org.opencontainers.image.source="https://github.com/vladmandic/sdnext/" \
      org.opencontainers.image.licenses="AGPL-3.0" \
      org.opencontainers.image.title="SD.Next ROCm" \
      org.opencontainers.image.description="SD.Next with ROCm 7.2 runtime" \
      org.opencontainers.image.base.name="rocm/dev-ubuntu-24.04"

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_PREFER_BINARY=1 \
    UV_NO_CACHE=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SD_DOCKER=true \
    SD_DATADIR=/mnt/data \
    SD_MODELSDIR=/mnt/models \
    venv_dir=/mnt/python/venv \
    ROCM_TORCH_INDEX=${rocm_torch_index} \
    TORCH_COMMAND="pip install --index-url ${rocm_torch_index} ${torch_packages}" \
    HSA_ENABLE_SDMA=0 \
    PYTORCH_HIP_ALLOC_CONF=expandable_segments:True \
    LD_PRELOAD=libjemalloc.so.2

RUN set -eux; \
    apt-get update -y; \
    apt-get install --no-install-recommends -y \
        bash \
        build-essential \
        ca-certificates \
        curl \
        ffmpeg \
        git \
        gpg \
        libgl1 \
        libglib2.0-0 \
        libjemalloc-dev \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        software-properties-common \
        tini \
        wget; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    mkdir -p "${app_dir}" /mnt/data /mnt/models /mnt/python /root/.cache/huggingface

RUN set -eux; \
    printf '%s\n' \
      '#!/usr/bin/env bash' \
      'set -euo pipefail' \
      '' \
      'APP_DIR="${APP_DIR:-/app}"' \
      'SDNEXT_REPO="${SDNEXT_REPO:-https://github.com/vladmandic/sdnext.git}"' \
      'SDNEXT_REF="${SDNEXT_REF:-master}"' \
      '' \
      'if [[ ! -d "${APP_DIR}/.git" ]]; then' \
      '  mkdir -p "${APP_DIR}"' \
      '  git clone --depth 1 --branch "${SDNEXT_REF}" "${SDNEXT_REPO}" "${APP_DIR}"' \
      'fi' \
      '' \
      'if [[ -x /opt/rocm/bin/rocminfo ]]; then' \
      '  if /opt/rocm/bin/rocminfo 2>/dev/null | grep -q "gfx1103" && [[ -z "${HSA_OVERRIDE_GFX_VERSION:-}" ]]; then' \
      '    export HSA_OVERRIDE_GFX_VERSION=11.0.0' \
      '    echo "[entrypoint] Detected gfx1103, set HSA_OVERRIDE_GFX_VERSION=${HSA_OVERRIDE_GFX_VERSION}"' \
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
      'cd "${APP_DIR}"' \
      'exec bash ./webui.sh -f --use-rocm --uv --listen --port 7860 --api-log --log sdnext.log "$@"' \
      > /usr/local/bin/startup.sh; \
    chmod +x /usr/local/bin/startup.sh

WORKDIR ${app_dir}
EXPOSE 7860
VOLUME ["/app", "/mnt/data", "/mnt/models", "/mnt/python", "/root/.cache/huggingface"]
STOPSIGNAL SIGINT

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/startup.sh"]
