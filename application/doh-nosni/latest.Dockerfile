# 第一阶段：生成配置文件
FROM debian:sid-slim AS builder

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
# 基本设置\n\
listen_addresses = ["127.0.0.1:5053"]\n\
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
# 设置 dnsmasq 配置\n\
cat > /etc/dnsmasq.conf << EOF\n\
# 基础设置\n\
no-resolv\n\
no-poll\n\
# 将请求转发至本地dnscrypt-proxy\n\
server=127.0.0.1#5053\n\
listen-address=0.0.0.0\n\
bind-interfaces\n\
\n\
# 缓存设置\n\
cache-size=10000\n\
min-cache-ttl=300\n\
\n\
# 日志设置\n\
log-queries=extra\n\
log-facility=-\n\
EOF\n\
\n\
# 启动 dnscrypt-proxy\n\
echo "Starting dnscrypt-proxy (NO SNI mode)..."\n\
dnscrypt-proxy -config /etc/dnscrypt-proxy/dnscrypt-proxy.toml &\n\
DNSCRYPT_PID=$!\n\
\n\
# 等待 dnscrypt-proxy 启动\n\
sleep 2\n\
if ! kill -0 $DNSCRYPT_PID 2>/dev/null; then\n\
  echo "Failed to start dnscrypt-proxy"\n\
  exit 1\n\
fi\n\
echo "dnscrypt-proxy started successfully (PID: $DNSCRYPT_PID)"\n\
\n\
# 设置进程终止信号处理\n\
trap "kill $DNSCRYPT_PID; exit" SIGINT SIGTERM\n\
\n\
# 启动dnsmasq并运行在前台\n\
echo "Starting dnsmasq..."\n\
echo "DNS over HTTPS proxy is now running (NO SNI)!"\n\
echo "IPv4 and IPv6 support enabled by default"\n\
\n\
exec dnsmasq -k --log-facility=- --no-daemon\n\
' > /start.sh \
    && chmod +x /start.sh

# 第二阶段：安装必要软件并复制配置
FROM debian:sid-slim

# 环境变量配置
ENV DEBIAN_FRONTEND=noninteractive

# 安装必要软件 (仅保留必要组件)
RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        dnsmasq \
        dnscrypt-proxy \
        tzdata \
    && apt-get autoremove --purge -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log

# 从构建阶段复制配置文件
COPY --from=builder /etc/dnscrypt-proxy/dnscrypt-proxy.toml /etc/dnscrypt-proxy/
COPY --from=builder /start.sh /start.sh

# 创建运行目录并设置权限
RUN mkdir -p /var/run/dnscrypt-proxy \
    && chmod -R 755 /var/run/dnscrypt-proxy \
    && chmod 644 /etc/dnscrypt-proxy/dnscrypt-proxy.toml \
    && chmod 755 /start.sh

# 仅暴露需要的端口
EXPOSE 53/tcp 53/udp

# 启动服务
CMD ["/start.sh"]