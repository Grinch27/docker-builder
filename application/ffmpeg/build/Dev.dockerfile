FROM ubuntu:devel AS buildstage

ARG FFMPEG_BRANCH=master
    # FFMPEG_VERSION=5.1.2 

ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/root/.cargo/bin:${PATH}"

# ========== install build packages ==========
RUN set -x \
    && apt-get update \
    && apt-get install -y -qq \
      autoconf \
      automake \
      bindgen \
      bison \
      build-essential \
      bzip2 \
      ca-certificates \
      cargo \
      cmake \
      curl \
      diffutils \
      doxygen \
      flex \
      g++ \
      gcc \
      git \
      gperf \
      i965-va-driver-shaders \
      intel-media-va-driver-non-free \
      less \
      libasound2-dev \
      libass-dev \
      libbluray-dev \
      libcairo2-dev \
      libelf-dev \
      libexpat1-dev \
      libgomp1 \
      libmfx-dev \
      libmfx-tools \
      libmfx1 \
      libpciaccess-dev \
      libssl-dev \
      libtool \
      libva-dev \
      libva-drm2 \
      libva-glx2 \
      libva-wayland2 \
      libva-x11-2 \
      libv4l-dev \
      libwayland-dev \
      libwayland-egl-backend-dev \
      libx11-xcb-dev \
      libx264-dev \
      libx265-dev \
      libxfixes-dev \
      libxml2-dev \
      libxrandr-dev \
      libxcb-dri2-0-dev \
      libxcb-dri3-dev \
      libxcb-glx0-dev \
      libxcb-present-dev \
      libxxf86vm-dev \
      locales \
      make \
      nasm \
      ocl-icd-opencl-dev \
      perl \
      pkg-config \
      pipx \
      python3-full \
      python3-pip \
      python3-venv \
      vainfo \
      wget \
      x11proto-gl-dev \
      x11proto-xext-dev \
      xxd \
      yasm \
    # ===== Clean apt =====
    && cargo install \
      cargo-c \
      cbindgen \
    # && python3 -m venv /lsiopy \
    # && pipx install \
    #   pip \
    #   setuptools \
    #   wheel \
    && pipx install \
      cmake \
      mako \
      meson \
      ninja \
      packaging \
      ply \
      pyyaml

# 下载并编译 FFmpeg
RUN set -x \
    && cd /tmp \
    && dir_ffmpeg="/tmp/ffmpeg" \
    && git clone https://git.ffmpeg.org/ffmpeg.git ${dir_ffmpeg} --branch=${FFMPEG_BRANCH} --single-branch --depth 1 \
    && cd ${dir_ffmpeg} \
    && ./configure \
       --enable-libmfx \
       --enable-nonfree \
       --enable-libbluray \
       --enable-fontconfig \
       --enable-libass \
       --enable-gpl \
       --enable-libx264 \
       --enable-libx265 \
       --enable-vaapi \
    # && make -j8 \
    && make -j$(nproc --all)
    # && make install
    
RUN set -x \
    # echo "**** arrange files ****"
    && /usr/local/lib/rustlib/uninstall.sh \
    && ldconfig \
    && mkdir -p \
      /buildout/usr/local/bin \
      /buildout/usr/local/etc/fonts \
      /buildout/usr/local/lib/libmfx-gen \
      /buildout/usr/local/lib/mfx \
      /buildout/usr/local/lib/x86_64-linux-gnu/dri \
      /buildout/usr/local/lib/x86_64-linux-gnu/vdpau \
      /buildout/usr/local/share/vulkan \
      /buildout/usr/share/fonts \
      /buildout/usr/share/libdrm \
      /buildout/etc/OpenCL/vendors \
    && cp \
      /tmp/ffmpeg/ffmpeg \
      /buildout/usr/local/bin



FROM ubuntu:devel

# Add files from binstage
COPY --from=buildstage /buildout/ /
ARG DEBIAN_FRONTEND="noninteractive"

# 设置环境变量 hardware env
ENV LIBVA_DRIVER_NAME=iHD \
    LIBVA_DRIVERS_PATH="/usr/local/lib/x86_64-linux-gnu/dri" \
    LD_LIBRARY_PATH="/usr/local/lib"

RUN set -x \
    # ===== install runtime =====
    && apt-get update \
    && apt-get install -y \
      libasound2t64 \
      libedit2 \
      libelf1 \
      libexpat1 \
      libglib2.0-0 \
      libgomp1 \
      libllvm18 \
      libpciaccess0 \
      libv4l-0 \
      libwayland-client0 \
      libx11-6 \
      libx11-xcb1 \
      libxcb-dri2-0 \
      libxcb-dri3-0 \
      libxcb-present0 \
      libxcb-randr0 \
      libxcb-shape0 \
      libxcb-shm0 \
      libxcb-sync1 \
      libxcb-xfixes0 \
      libxcb1 \
      libxext6 \
      libxfixes3 \
      libxshmfence1 \
      libxml2 \
      ocl-icd-libopencl1 \
    # ===== Clean apt =====
    && apt-get autoremove --purge -y -qq \
    && apt-get clean -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
    && rm -rf /var/tmp/* \
    # ===== test ffmpeg =====
    && ldd /usr/local/bin/ffmpeg \
    && /usr/local/bin/ffmpeg -version

# 设置工作目录
# WORKDIR /media
# COPY /root /

ENTRYPOINT ["uname -a", "sleep infinity"]
