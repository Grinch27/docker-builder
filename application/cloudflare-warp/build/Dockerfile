# 待确认：ubuntu:devel 与 WARP 的依赖、隧道、双架构和长期稳定性须实测。
# 歧义：“最新”指 CODENAME 对应的 Cloudflare 官方稳定仓库在下载阶段重新执行时的候选版本，不含 beta。
# 后续研究：Cloudflare 支持新的 Ubuntu 版本后评估默认 CODENAME。
# 潜在优化：下载工具和 Cloudflare 仓库仅留在 download 阶段；deb 不进入最终镜像层。
# 风险：devel 是滚动开发版，CODENAME 指 Cloudflare APT suite，两者兼容性须实测。
# 验证重点：APT 签名、目标架构、包元数据、依赖、CLI/daemon、临时文件清理。
# 运行要求：NET_ADMIN、/dev/net/tun，持久化 /var/lib/cloudflare-warp；手动注册连接。
# 缓存：获取最新包用 --no-cache-filter download；或传入新的 WARP_REFRESH 值。
# 更新基础镜像另加 --pull；代理只用 BuildKit 预定义 build args，不写入 ENV。
# 官方仓库：https://pkg.cloudflareclient.com/
# 需要 BuildKit。无需本地 deb；构建缓存可能保留 download 阶段，但最终镜像不包含它。

ARG base_image=ubuntu:devel
FROM ${base_image} AS download

ARG CODENAME=resolute
RUN set -eu; \
    . /etc/os-release; \
    test "$ID" = ubuntu; \
    case "$(dpkg --print-architecture)" in amd64|arm64) ;; *) exit 1 ;; esac; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get -o APT::Update::Error-Mode=any update; \
    apt-get install -y --no-install-recommends ca-certificates curl; \
    install -m 0755 -d /etc/apt/keyrings; \
    curl -fsSL --retry 3 --connect-timeout 15 --max-time 120 \
      https://pkg.cloudflareclient.com/pubkey.gpg \
      -o /etc/apt/keyrings/cloudflare-warp.asc; \
    chmod a+r /etc/apt/keyrings/cloudflare-warp.asc; \
    printf 'deb [arch=%s signed-by=/etc/apt/keyrings/cloudflare-warp.asc] https://pkg.cloudflareclient.com/ %s main\n' \
      "$(dpkg --print-architecture)" "$CODENAME" \
      > /etc/apt/sources.list.d/cloudflare-client.list; \
    rm -rf /var/lib/apt/lists/*

ARG WARP_REFRESH=default
RUN set -eu; \
    : "$WARP_REFRESH"; \
    apt-get -o APT::Update::Error-Mode=any \
      -o Dir::Etc::sourcelist=/etc/apt/sources.list.d/cloudflare-client.list \
      -o Dir::Etc::sourceparts=- update; \
    install -d -m 0755 -o _apt -g root /out; \
    cd /out; \
    apt-get download cloudflare-warp; \
    set -- ./cloudflare-warp_*.deb; \
    test "$#" -eq 1; \
    test -s "$1"; \
    test "$(dpkg-deb -f "$1" Package)" = cloudflare-warp; \
    test "$(dpkg-deb -f "$1" Architecture)" = "$(dpkg --print-architecture)"; \
    dpkg-deb -f "$1" Package Version Architecture Depends; \
    mv "$1" /out/cloudflare-warp.deb; \
    chmod 0644 /out/cloudflare-warp.deb; \
    rm -rf /var/lib/apt/lists/*

FROM ${base_image} AS runtime

# 使用阶段挂载；临时复制、安装、删除发生在同一个 RUN，避免 COPY 留下 deb 层。
RUN --mount=type=bind,from=download,source=/out,target=/mnt/warp,readonly \
    set -eu; \
    . /etc/os-release; \
    test "$ID" = ubuntu; \
    cp /mnt/warp/cloudflare-warp.deb /tmp/cloudflare-warp.deb; \
    test "$(dpkg-deb -f /tmp/cloudflare-warp.deb Package)" = cloudflare-warp; \
    test "$(dpkg-deb -f /tmp/cloudflare-warp.deb Architecture)" = "$(dpkg --print-architecture)"; \
    warp_version="$(dpkg-deb -f /tmp/cloudflare-warp.deb Version)"; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get -o APT::Update::Error-Mode=any update; \
    apt-get install -y --no-install-recommends --no-install-suggests \
      /tmp/cloudflare-warp.deb; \
    test "$(dpkg-query -W -f='${Version}' cloudflare-warp)" = "$warp_version"; \
    test "$(dpkg-query -W -f='${Status}' cloudflare-warp)" = 'install ok installed'; \
    test -z "$(dpkg --audit)"; \
    warp-cli --version; \
    test -x /bin/warp-svc; \
    install -d -m 0700 /var/lib/cloudflare-warp; \
    rm -f /tmp/cloudflare-warp.deb; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/bin/warp-svc"]
