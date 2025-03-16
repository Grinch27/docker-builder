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
listen_addresses = [\"0.0.0.0:53\"]\n\
max_clients = 100\n\
\n\
# 服务器选择\n\
server_names = [\"cloudflare\", \"cloudflare-ipv6\"]\n\
\n\
# 隐私保护设置\n\
tls_disable_session_tickets = true\n\
dnscrypt_ephemeral_keys = false\n\
bootstrap_resolvers = [\"1.1.1.1:53\"]\n\
\n\
# 连接设置\n\
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
# 日志设置\n\
log_level = 2\n\
log_file = \"\"\n\
use_syslog = false\n\
\n\
# IPv4/IPv6 设置\n\
ipv4_servers = true\n\
ipv6_servers = false\n\
block_ipv6 = false\n\
block_unqualified = false\n\
block_undelegated = false\n\
reject_ttl = 600\n\
ignore_system_dns = true\n\
\n\
# 静态服务器定义\n\
[sources]\n\
\n\
[static]\n\
  [static.\"cloudflare\"]\n\
  stamp = \"sdns://AgcAAAAAAAAABzEuMC4wLjEABzEuMC4wLjEKL2Rucy1xdWVyeQ\"\n\
\n\
  [static.\"cloudflare-ipv6\"]\n\
  stamp = \"sdns://AgcAAAAAAAAAFlsyNjA2OjQ3MDA6OjY4MTA6ZjlmOV0AEmNsb3VkZmxhcmUtZG5zLmNvbQovZG5zLXF1ZXJ5\"\n\
' > /etc/dnscrypt-proxy/dnscrypt-proxy.toml

# 创建启动脚本
RUN echo '#!/bin/bash\n\
\n\
uname -a\n\
\n\
set -e\n\
\n\
exec dnscrypt-proxy --config /etc/dnscrypt-proxy/dnscrypt-proxy.toml\n\
\n\
set +e\n\
\n\
& sleep infinity\n\
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

# uname -a && exec dnscrypt-proxy -config /etc/dnscrypt-proxy/dnscrypt-proxy.toml && sleep infinity
ENTRYPOINT ["/start.sh"]
