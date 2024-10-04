FROM ubuntu:devel AS buildstage

ARG DEBIAN_FRONTEND=noninteractive \
    FFMPEG_BRANCH=master
    # FFMPEG_VERSION=5.1.2

# 更新并安装依赖
RUN set -x \
    && apt-get update \
    && apt-get install -y -qq \
      cmake \
      ca-certificates \
      curl \
      gcc \
      g++ \
      git \
      intel-media-va-driver-non-free \
      less \
      libass-dev \
      libbluray-dev \
      libmfx-dev \
      libmfx-tools \
      libmfx1 \
      libva-dev \
      libva-drm2 \
      libva-glx2 \
      libva-wayland2 \
      libva-x11-2 \
      libx264-dev \
      libx265-dev \
      locales \
      pkg-config \
      python3-full \
      python3-pip \
      python3-xyz \
      vainfo \
      vim \
      wget \
      yasm

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
# ENV LC_ALL=C.UTF-8
# ENV LANG=C.UTF-8
ENV \
  LIBVA_DRIVER_NAME=iHD \
  LIBVA_DRIVERS_PATH="/usr/local/lib/x86_64-linux-gnu/dri" \
  LD_LIBRARY_PATH="/usr/local/lib" \

# 配置本地化
# RUN echo "C.UTF-8 UTF-8" >> /etc/locale.gen \
#     && locale-gen


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
