# 第一阶段：生成配置文件和证书
ARG base_image=debian:sid-slim
FROM ${base_image} AS builder

# 安装生成证书所需的软件
RUN set -x \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        openssl \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log

# 创建证书目录并生成自签名证书
RUN mkdir -p /etc/nginx/ca \
    && openssl req -x509 -nodes -days 3650 \
    -newkey rsa:2048 \
    -keyout /etc/nginx/ca/DOH_NO_SNI.key \
    -out /etc/nginx/ca/DOH_NO_SNI.crt \
    -subj "/CN=DOH_NO_SNI" \
    -addext "subjectAltName=DNS:dns.cloudflare.com"

# 创建精简的 DOH_NO_SNI.conf 配置
RUN echo "# DNS over HTTPS proxy configuration\n\
\n\
# Local DNS-DOH bridge\n\
server {\n\
    listen 8053;\n\
    location /dns-query {\n\
        proxy_pass https://real-cloudflare-dns;\n\
        proxy_set_header Host \$http_host;\n\
        proxy_set_header User-Agent \$http_user_agent;\n\
        proxy_set_header X-Real-IP \$remote_addr;\n\
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\n\
        proxy_ssl_server_name off;\n\
        proxy_buffering off;\n\
        proxy_connect_timeout 10;\n\
        proxy_send_timeout 10;\n\
        proxy_read_timeout 10;\n\
    }\n\
}\n\
\n\
# 真实的Cloudflare DNS - 使用IP地址避免循环代理\n\
upstream real-cloudflare-dns {\n\
    server 1.1.1.1:443;\n\
    server 1.0.0.1:443;\n\
    server [2606:4700:4700::1111]:443;\n\
    server [2606:4700:4700::1001]:443;\n\
}\n\
\n\
server {\n\
    listen 443 ssl;\n\
    server_name dns.cloudflare.com;\n\
\n\
    ssl_certificate ca/DOH_NO_SNI.crt;\n\
    ssl_certificate_key ca/DOH_NO_SNI.key;\n\
    ssl_protocols TLSv1.3 TLSv1.2;\n\
\n\
    location / {\n\
        proxy_pass https://real-cloudflare-dns;\n\
        proxy_set_header Host \$http_host;\n\
        proxy_set_header User-Agent \$http_user_agent;\n\
        proxy_set_header X-Real-IP \$remote_addr;\n\
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\n\
        proxy_ssl_server_name off;\n\
        proxy_buffering off;\n\
    }\n\
}" > /etc/nginx/conf.d/DOH_NO_SNI.conf

# 创建启动脚本
RUN echo '#!/bin/bash\n\
# 设置 dnsmasq 配置\n\
cat > /etc/dnsmasq.conf << EOF\n\
no-resolv\n\
no-poll\n\
server=127.0.0.1#8053\n\
listen-address=0.0.0.0\n\
cache-size=${CACHE_SIZE:-1000}\n\
log-queries=extra\n\
log-facility=-\n\
EOF\n\
\n\
echo "Starting DNS proxy with Cloudflare Standard (NO SNI)"\n\
echo "IPv4 and IPv6 support enabled by default"\n\
echo "DNS server dns.cloudflare.com is mapped to 127.0.0.1 in hosts file"\n\
\n\
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf\n\
' > /start.sh \
    && chmod +x /start.sh

# 创建 supervisor 配置
RUN echo '[supervisord]\n\
nodaemon=true\n\
user=root\n\
\n\
[program:nginx]\n\
command=nginx -g "daemon off;"\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
\n\
[program:dnsmasq]\n\
command=dnsmasq -k\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
' > /etc/supervisor/conf.d/supervisord.conf

# 第二阶段：安装必要软件并复制配置
ARG base_image=debian:sid-slim
FROM ${base_image} AS builder

# 环境变量配置
ENV DEBIAN_FRONTEND=noninteractive \
    CACHE_SIZE=1000 \
    TZ="Asia/Shanghai"

# 安装必要软件
RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        nginx-full \
        dnsmasq \
        supervisor \
    && apt-get autoremove --purge -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
    && rm -f /etc/nginx/sites-enabled/default

# 从构建阶段复制证书和配置文件
COPY --from=builder /etc/nginx/ca /etc/nginx/ca
COPY --from=builder /etc/nginx/conf.d/DOH_NO_SNI.conf /etc/nginx/conf.d/
COPY --from=builder /start.sh /start.sh
COPY --from=builder /etc/supervisor/conf.d/supervisord.conf /etc/supervisor/conf.d/

# 修改 hosts 文件，将上游 DNS 服务器指向本地
RUN echo "127.0.0.1 dns.cloudflare.com" >> /etc/hosts

# 确保文件权限
RUN chmod -R 755 /etc/nginx/ca \
    && chmod 644 /etc/nginx/ca/DOH_NO_SNI.crt \
    && chmod 600 /etc/nginx/ca/DOH_NO_SNI.key \
    && chmod 644 /etc/nginx/conf.d/DOH_NO_SNI.conf \
    && chmod 755 /start.sh \
    && chmod 644 /etc/supervisor/conf.d/supervisord.conf

# # 健康检查
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD dig @127.0.0.1 -p 53 cloudflare.com || exit 1

# 仅暴露需要的端口
EXPOSE 53/tcp 53/udp

# 启动服务
CMD ["/start.sh"]