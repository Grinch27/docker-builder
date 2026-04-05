# SD.Next ROCm Dockerfile
# docs: <https://github.com/vladmandic/sdnext/wiki/Docker>

# base image

# rocm runtime (recommended for general use)
ARG base_image=rocm/dev-ubuntu-24.04
FROM ${base_image}

# rocm complete (very large), required to build flash-attn and similar kernels
# build example:
# docker build --build-arg base_image=rocm/dev-ubuntu-24.04:7.2.0-complete .

# metadata
LABEL org.opencontainers.image.vendor="SD.Next"
LABEL org.opencontainers.image.authors="docker-builder"
LABEL org.opencontainers.image.url="https://github.com/vladmandic/sdnext/"
LABEL org.opencontainers.image.documentation="https://github.com/vladmandic/sdnext/wiki/Docker"
LABEL org.opencontainers.image.source="https://github.com/vladmandic/sdnext/"
LABEL org.opencontainers.image.licenses="AGPL-3.0"
LABEL org.opencontainers.image.title="SD.Next ROCm"
LABEL org.opencontainers.image.description="SD.Next with ROCm 7.2 runtime"
LABEL org.opencontainers.image.base.name="https://hub.docker.com/r/rocm/dev-ubuntu-24.04"
LABEL org.opencontainers.image.version="latest"

ARG DEBIAN_FRONTEND=noninteractive
ARG sdnext_repo=https://github.com/vladmandic/sdnext.git
ARG sdnext_ref=master
ARG app_dir=/app
ARG rocm_torch_index=https://download.pytorch.org/whl/rocm7.2
ARG torch_packages="torch==2.11.0+rocm7.2 torchvision==0.26.0+rocm7.2"
ARG gradio_version=3.43.2
ARG gradio_client_version=0.5.0
ARG build_arg=""

# fix for startup.sh
ENV APP_DIR=${app_dir}
ENV SDNEXT_REPO=${sdnext_repo}
ENV SDNEXT_REF=${sdnext_ref}

# essentials
RUN apt-get update && \
    apt-get install -y --no-install-recommends --fix-missing \
    software-properties-common \
    build-essential \
    ca-certificates \
    wget \
    gpg \
    git \
    curl \
    ffmpeg \
    bash \
    libgl1 \
    libglib2.0-0 \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
    libjemalloc-dev && \
    /usr/sbin/ldconfig && \
    # ===== Clean apt =====
    && apt-get autoremove --purge -y -qq \
    && apt-get clean -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
	# && unset DEBIAN_FRONTEND \

# jemalloc is not required but it is highly recommended
ENV LD_PRELOAD=libjemalloc.so.2

# stop pip and uv from caching
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_PREFER_BINARY=1
ENV UV_NO_CACHE=true

# set paths to use with sdnext
ENV SD_DOCKER=true
ENV SD_DATADIR="/mnt/data"
ENV SD_MODELSDIR="/mnt/models"
ENV venv_dir="/mnt/python/venv"
ENV ROCM_TORCH_INDEX=${rocm_torch_index}
ENV TORCH_COMMAND="${torch_packages} --index-url ${rocm_torch_index}"
ENV HSA_ENABLE_SDMA=0
ENV PYTORCH_HIP_ALLOC_CONF=expandable_segments:True
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

### copilot fix
ENV GIT_TERMINAL_PROMPT=0
# ENV PIP_DEFAULT_TIMEOUT=180
ENV VIRTUAL_ENV=${venv_dir}
ENV PATH=${venv_dir}/bin:${PATH}

# paths used by sdnext can be a volume if necessary
# VOLUME [ "/app" ]
# VOLUME [ "/mnt/data" ]
# VOLUME [ "/mnt/models" ]
# VOLUME [ "/mnt/python" ]
# VOLUME [ "/root/.cache/huggingface" ]
# RUN mkdir -p "${app_dir}" /mnt/data /mnt/models /mnt/python /root/.cache/huggingface

# override gpu architecture for unsupported gpus
# ENV HSA_OVERRIDE_GFX_VERSION=10.0.0

# git clone and run sdnext
### copilot fix
RUN mkdir -p "${app_dir}" /mnt/data /mnt/models /mnt/python /root/.cache/huggingface && \
    chmod 0777 "${app_dir}" /mnt/data /mnt/models /mnt/python && \
    git clone --depth 1 --branch "${sdnext_ref}" "${sdnext_repo}" "${app_dir}" && \
    python3 -m venv "${venv_dir}" && \
    "${venv_dir}/bin/python" -m pip install --upgrade pip setuptools wheel uv && \
    "${venv_dir}/bin/python" -m pip install --no-deps \
        "compel==2.3.1" \
        "gradio==${gradio_version}" \
        "gradio-client==${gradio_client_version}" && \
    "${venv_dir}/bin/python" -m pip install --constraint "${app_dir}/constraints.txt" \
        addict \
        hf_transfer \
        fastapi \
        websockets \
        aiofiles \
        ffmpy \
        onnx \
        onnxruntime \
        pydub \
        uvicorn \
        semantic-version \
        altair \
        python-multipart \
        matplotlib \
        yapf && \
    "${venv_dir}/bin/python" -m pip install --index-url "${rocm_torch_index}" ${torch_packages} && \
    "${venv_dir}/bin/python" -m pip install --constraint "${app_dir}/constraints.txt" -r "${app_dir}/requirements.txt" && \
    "${venv_dir}/bin/python" -m pip cache purge

COPY startup.sh /bin/startup.sh
RUN chmod 755 /bin/startup.sh

# actually run sdnext
WORKDIR /home
ENTRYPOINT [ "/bin/startup.sh", "-f", "--use-rocm", "--uv", "--listen", "--debug", "--api-log", "--log", "sdnext.log" ]

# expose port
EXPOSE 7860

# healthcheck function
# HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 CMD curl --fail http://localhost:7860/sdapi/v1/status || exit 1

# stop signal
STOPSIGNAL SIGINT
