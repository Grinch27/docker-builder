ARG base_image=alpine:edge
FROM ${base_image} AS builder

# 安装基本工具
RUN set -x \
    && apk update \
    && apk add --no-cache \
        ca-certificates \
    && rm -rf /var/cache/apk/* \
    && rm -rf /var/log/*.log

# 创建 dnscrypt-proxy 配置 - 关闭 SNI
RUN mkdir -p /etc/dnscrypt-proxy \
        && cat << 'EOF' > /etc/dnscrypt-proxy/dnscrypt-proxy.toml
listen_addresses = ["0.0.0.0:53"]
max_clients = 100

# 服务器选择
server_names = ["cloudflare", "cloudflare-ipv6"]

# 隐私保护设置
tls_disable_session_tickets = true
dnscrypt_ephemeral_keys = false
bootstrap_resolvers = ["1.1.1.1:53"]

# 连接设置
force_tcp = false
timeout = 5000
keepalive = 30

# 缓存设置
cache = true
cache_size = 8192
cache_min_ttl = 300
cache_max_ttl = 86400
cache_neg_min_ttl = 60
cache_neg_max_ttl = 600

# 日志设置
log_level = 2
log_file = ""
use_syslog = false

# IPv4/IPv6 设置
ipv4_servers = true
ipv6_servers = true
block_ipv6 = false
block_unqualified = false
block_undelegated = false
reject_ttl = 600
ignore_system_dns = true

# 静态服务器定义
[sources]

[static]
    [static."cloudflare"]
    stamp = "sdns://AgcAAAAAAAAABzEuMC4wLjEABzEuMC4wLjEKL2Rucy1xdWVyeQ"

    [static."cloudflare-ipv6"]
    stamp = "sdns://AgcAAAAAAAAAFlsyNjA2OjQ3MDA6OjY4MTA6ZjlmOV0AEmNsb3VkZmxhcmUtZG5zLmNvbQovZG5zLXF1ZXJ5"
EOF

# 创建启动脚本
RUN cat << 'EOF' > /start.sh
#!/bin/sh

set -e

exec dnscrypt-proxy --config /etc/dnscrypt-proxy/dnscrypt-proxy.toml
EOF \
    && chmod +x /start.sh

# 第二阶段：安装必要软件并复制配置
FROM ${base_image}

# 安装必要软件 (仅保留必要组件)
RUN set -x \
    && apk update \
    && apk add --no-cache \
        ca-certificates \
        dnscrypt-proxy \
    && rm -rf /var/cache/apk/* \
    && rm -rf /var/log/*.log

# 从构建阶段复制配置文件
COPY --from=builder /etc/dnscrypt-proxy/dnscrypt-proxy.toml /etc/dnscrypt-proxy/
COPY --from=builder /start.sh /start.sh

# 设置权限
RUN chmod 644 /etc/dnscrypt-proxy/dnscrypt-proxy.toml \
    && chmod 755 /start.sh

# # 仅暴露需要的端口
# EXPOSE 53/tcp 53/udp

ENTRYPOINT ["/start.sh"]
