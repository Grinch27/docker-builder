ARG base_image=debian:sid-slim
FROM ${base_image} AS builder

# 安装基本工具
RUN set -x \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log

# 创建 dnscrypt-proxy 配置 - 关闭 SNI
RUN mkdir -p /etc/dnscrypt-proxy \
    && echo '\
# dnscrypt-proxy 配置 - 无SNI泄露\n\
\n\
# 基本设置 - 直接监听53端口\n\
listen_addresses = ["0.0.0.0:53"]\n\
max_clients = 250\n\
ipv4_servers = true\n\
ipv6_servers = true\n\
\n\
# 隐私保护设置\n\
tls_disable_session_tickets = true\n\
esni = true\n\
\n\
# 服务器选择 - 使用安全的无SNI实现\n\
force_tcp = false\n\
timeout = 5000\n\
keepalive = 30\n\
\n\
# 缓存设置\n\
cache = true\n\
cache_size = 4096\n\
cache_min_ttl = 300\n\
cache_max_ttl = 86400\n\
cache_neg_min_ttl = 60\n\
cache_neg_max_ttl = 600\n\
\n\
# 使用Cloudflare服务器\n\
server_names = ["cloudflare"]\n\
\n\
[static]\n\
  [static."cloudflare"]\n\
  stamp = "sdns://AgcAAAAAAAAACzEwNC4xOS4xOTkuMjMAG3NsLWRvaC5jaXJjbC5vcGVuZG5zLmNvbS93Zy1zdGFnaW5n"\n\
\n\
# 日志设置\n\
log_level = 2\n\
log_file = ""\n\
use_syslog = false\n\
\n\
# 禁用所有需要域名查询的功能\n\
block_ipv6 = false\n\
block_unqualified = false\n\
block_undelegated = false\n\
reject_ttl = 600\n\
' > /etc/dnscrypt-proxy/dnscrypt-proxy.toml

# 创建启动脚本
RUN echo '#!/bin/bash\n\
\n\
set -e\n\
\n\
uname -a\n\
\n\
exec dnscrypt-proxy --config /etc/dnscrypt-proxy/dnscrypt-proxy.toml\n\
\n\
set +e\n\
sleep infinity\n\
' > /start.sh \
    && chmod +x /start.sh

# 第二阶段：安装必要软件并复制配置
FROM ${base_image}

# 环境变量配置
ENV DEBIAN_FRONTEND=noninteractive 

# 安装必要软件 (仅保留必要组件)
RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        dnscrypt-proxy \
    && apt-get autoremove --purge -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log

# 从构建阶段复制配置文件
COPY --from=builder /etc/dnscrypt-proxy/dnscrypt-proxy.toml /etc/dnscrypt-proxy/
COPY --from=builder /start.sh /start.sh

# 设置权限
RUN chmod 644 /etc/dnscrypt-proxy/dnscrypt-proxy.toml \
    && chmod 755 /start.sh

# 仅暴露需要的端口
EXPOSE 53/tcp 53/udp

# 启动服务
# uname -a && exec dnscrypt-proxy -config /etc/dnscrypt-proxy/dnscrypt-proxy.toml && sleep infinity
ENTRYPOINT ["/start.sh"]