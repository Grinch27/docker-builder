# SD.Next ROCm Dockerfile (TheRock tarball experimental)
# docs: <https://github.com/vladmandic/sdnext/wiki/Docker>

# Experimental image: system ROCm comes from a TheRock tarball while the
# existing SD.Next dependency flow stays close to the current production image.

ARG base_image=ubuntu:24.04
FROM ${base_image}

LABEL org.opencontainers.image.vendor="SD.Next"
LABEL org.opencontainers.image.authors="docker-builder"
LABEL org.opencontainers.image.url="https://github.com/vladmandic/sdnext/"
LABEL org.opencontainers.image.documentation="https://github.com/vladmandic/sdnext/wiki/Docker"
LABEL org.opencontainers.image.source="https://github.com/vladmandic/sdnext/"
LABEL org.opencontainers.image.licenses="AGPL-3.0"
LABEL org.opencontainers.image.title="SD.Next ROCm (TheRock experimental)"
LABEL org.opencontainers.image.description="SD.Next with a TheRock tarball ROCm runtime for gfx110X experiments"
LABEL org.opencontainers.image.base.name="${base_image}"
LABEL org.opencontainers.image.version="dev"

ARG DEBIAN_FRONTEND=noninteractive
ARG sdnext_repo=https://github.com/vladmandic/sdnext.git
ARG sdnext_ref=master
ARG app_dir=/app
ARG venv_dir=/mnt/python/venv
ARG therock_version=7.10.0
ARG therock_amdgpu_family=gfx110X-all
ARG therock_release_type=stable
ARG rocm_torch_index=https://download.pytorch.org/whl/rocm7.2
ARG torch_packages="torch==2.11.0+rocm7.2 torchvision==0.26.0+rocm7.2"
ARG build_arg=""

ENV APP_DIR=${app_dir}
ENV SDNEXT_REPO=${sdnext_repo}
ENV SDNEXT_REF=${sdnext_ref}
ENV LD_PRELOAD=libjemalloc.so.2
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_PREFER_BINARY=1
ENV UV_NO_CACHE=true
ENV SD_DOCKER=true
ENV SD_DATADIR=/mnt/data
ENV SD_MODELSDIR=/mnt/models
ENV venv_dir=${venv_dir}
ENV ROCM_PATH=/opt/rocm
ENV ROCM_TORCH_INDEX=${rocm_torch_index}
ENV TORCH_COMMAND="${torch_packages} --index-url ${rocm_torch_index}"
ENV HSA_ENABLE_SDMA=0
ENV PYTORCH_HIP_ALLOC_CONF=expandable_segments:True
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GIT_TERMINAL_PROMPT=0
ENV VIRTUAL_ENV=${venv_dir}
ENV PATH=${venv_dir}/bin:/opt/rocm/bin:${PATH}
ENV LD_LIBRARY_PATH=/opt/rocm/lib:/opt/rocm/lib64

COPY install_therock_deps.sh /tmp/install_therock_deps.sh
COPY install_therock_tarball.sh /tmp/install_therock_tarball.sh

RUN set -eux; \
    therock_version="${therock_version}"; \
    therock_amdgpu_family="${therock_amdgpu_family}"; \
    therock_release_type="${therock_release_type}"; \
    rocm_torch_index="${rocm_torch_index}"; \
    torch_packages="${torch_packages}"; \
    build_arg=$(printf '%s' "${build_arg}" | sed 's|^[\"]*||;s|[\"]*$||' | sed "s|^[\']*||;s|[\']*$||"); \
    if [ -n "${build_arg}" ]; then \
      printf '%s\n' "${build_arg}" | tr ',' '\n' > /tmp/build.env; \
      while IFS='=' read -r key value; do \
        [ -n "${key}" ] || continue; \
        case "${key}" in \
          therock_version) therock_version="${value}" ;; \
          therock_amdgpu_family) therock_amdgpu_family="${value}" ;; \
          therock_release_type) therock_release_type="${value}" ;; \
          rocm_torch_index) rocm_torch_index="${value}" ;; \
          torch_packages) torch_packages="${value}" ;; \
        esac; \
      done < /tmp/build.env; \
      rm -f /tmp/build.env; \
    fi; \
    chmod +x /tmp/install_therock_deps.sh /tmp/install_therock_tarball.sh; \
    /tmp/install_therock_deps.sh; \
    /tmp/install_therock_tarball.sh "${therock_version}" "${therock_amdgpu_family}" "${therock_release_type}"; \
    mkdir -p "${app_dir}" /mnt/data /mnt/models /mnt/python /root/.cache/huggingface; \
    chmod 0777 "${app_dir}" /mnt/data /mnt/models /mnt/python; \
    git clone --depth 1 --branch "${sdnext_ref}" "${sdnext_repo}" "${app_dir}"; \
    python3 -m venv "${venv_dir}"; \
    "${venv_dir}/bin/python" -m pip install --upgrade pip setuptools wheel uv; \
    "${venv_dir}/bin/python" -m pip install --no-deps \
      "compel==2.3.1" \
      "gradio==3.43.2" \
      "gradio-client==0.5.0"; \
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
      yapf; \
    "${venv_dir}/bin/python" -m pip install --index-url "${rocm_torch_index}" ${torch_packages}; \
    "${venv_dir}/bin/python" -m pip install --constraint "${app_dir}/constraints.txt" -r "${app_dir}/requirements.txt"; \
    "${venv_dir}/bin/python" -m pip cache purge; \
    printf '%s\n' "${therock_version}" > /etc/therock-version; \
    printf '%s\n' \
      '#!/bin/sh' \
      "export THEROCK_VERSION=${therock_version}" \
      "export THEROCK_AMDGPU_FAMILY=${therock_amdgpu_family}" \
      "export THEROCK_RELEASE_TYPE=${therock_release_type}" \
      > /etc/profile.d/therock-env.sh; \
    chmod 644 /etc/profile.d/therock-env.sh; \
    rm -f /tmp/install_therock_deps.sh /tmp/install_therock_tarball.sh

COPY startup.sh /bin/startup.sh
RUN chmod 755 /bin/startup.sh

WORKDIR /home
ENTRYPOINT ["/bin/startup.sh", "-f", "--use-rocm", "--uv", "--listen", "--debug", "--api-log", "--log", "sdnext.log"]

EXPOSE 7860

STOPSIGNAL SIGINT