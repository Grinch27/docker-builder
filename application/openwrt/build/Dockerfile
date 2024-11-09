############################################################
# base on Debian/Ubuntu
############################################################

# ========== Stage1: downloader ==========
FROM debian:sid-slim AS downloader
RUN set -x \
    # ===== apt dependencies =====
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
        ca-certificates \
        curl \
        gpg \
        jq \
    # ===== Download OpenWrt from Repo =====
    && tag_releases="x86_64 main" \
    && name_target="generic-rootfs" \
    # 构建关键词的正则表达式模式
    && pattern=$(echo "$tag_releases" | tr ' ' '|') \
    # 获取最新匹配的 tag
    && tag_target=$(curl -s "https://api.github.com/repos/Grinch27/openwrt-compiler/tags" | \
        jq -r --arg pattern "$pattern" '.[] | select(.name | test($pattern)) | .name' | head -n 1) \
    # 获取对应 tag 下的下载链接
    && URL_download=$(curl -s "https://api.github.com/repos/Grinch27/openwrt-compiler/releases/tags/${tag_target}" | \
        jq -r --arg name_target "$name_target" '.assets[] | select(.name | contains($name_target)) | .browser_download_url' | head -n 1)  \
    # ----- Download -----
    && FILE_download="/tmp/rootfs.tar.gz" \
    && PATH_rootfs="/rootfs" \
    && mkdir -p ${PATH_rootfs} \
    && curl -fsSL ${URL_download} -o ${FILE_download} \
    && tar -xzf ${FILE_download} -C ${PATH_rootfs}

# ========== Stage2: extractor ==========
# FROM debian:sid-slim as extractor
FROM scratch
COPY --from=downloader /rootfs /
# ADD rootfs.tar.gz /
CMD ["sh", "-c", "sleep infinity"]
# CMD ["/sbin/init"]
