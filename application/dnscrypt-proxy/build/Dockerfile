ARG base_image=alpine:edge
FROM ${base_image}

# 安装必要软件 (仅保留必要组件)
RUN set -x \
    && apk update \
    && apk add --no-cache \
        ca-certificates \
        dnscrypt-proxy \
    && rm -rf /var/cache/apk/* \
    && rm -rf /var/log/*.log

# 复制配置文件和启动脚本
COPY dnscrypt-proxy.toml /etc/dnscrypt-proxy/dnscrypt-proxy.toml
COPY start.sh /start.sh

# 设置权限
RUN chmod 644 /etc/dnscrypt-proxy/dnscrypt-proxy.toml \
    && chmod 755 /start.sh

# # 仅暴露需要的端口
# EXPOSE 53/tcp 53/udp

ENTRYPOINT ["/start.sh"]
