# NOTE(agent): 当前按 GitHub Releases 网页列表顺序筛选最新的 main+x86_64 tag，再拼接 openwrt-x86-64-generic-rootfs.tar.gz 下载地址，不再用 tags 接口或 releases API 做筛选。
# NOTE(agent): 需要你确认是否要把 branch_target、arch_target、asset_filename 抽成 ARG；当前先固定 main / x86_64 / openwrt-x86-64-generic-rootfs.tar.gz 以匹配你给出的网页规则。
# NOTE(agent): 可优化点，如果后续要支持 openwrt-25.12 或更多 target，建议把 release 过滤逻辑提取成独立脚本，避免 Dockerfile 的 RUN 行继续变长。
############################################################
# base on Debian/Ubuntu
############################################################

# ========== Stage1: downloader ==========
FROM ubuntu:devel AS downloader
RUN set -x \
    # ===== apt dependencies =====
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
        ca-certificates \
        curl \
        gpg \
    # ===== Download OpenWrt from Repo =====
    && branch_target="main" \
    && arch_target="x86_64" \
    && asset_filename="openwrt-x86-64-generic-rootfs.tar.gz" \
    && releases_url="https://github.com/Grinch27/openwrt-compiler/releases" \
    # 按 GitHub Releases 网页顺序抓取最新的 main+x86_64 tag。
    && tag_path=$(curl --retry 3 --retry-all-errors --retry-delay 2 \
        -H 'User-Agent: docker-builder-openwrt' \
        -fsSL "${releases_url}" | \
        grep -oE '/Grinch27/openwrt-compiler/releases/tag/main%2B[^"?# ]*%2Bx86_64' | head -n 1) \
    && [ -n "${tag_path}" ] \
    && tag_target="${tag_path##*/}" \
    && URL_download="https://github.com/Grinch27/openwrt-compiler/releases/download/${tag_target}/${asset_filename}" \
    # ----- Download -----
    && FILE_download="/tmp/rootfs.tar.gz" \
    && PATH_rootfs="/rootfs" \
    && mkdir -p ${PATH_rootfs} \
    && curl --retry 3 --retry-all-errors --retry-delay 2 \
        -H 'User-Agent: docker-builder-openwrt' \
        -fsSL ${URL_download} -o ${FILE_download} \
    && tar -xzf ${FILE_download} -C ${PATH_rootfs}

# ========== Stage2: extractor ==========
# FROM debian:sid-slim as extractor
FROM scratch
COPY --from=downloader /rootfs /
# ADD rootfs.tar.gz /
CMD ["sh", "-c", "sleep infinity"]
# CMD ["/sbin/init"]
