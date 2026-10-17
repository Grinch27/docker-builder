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

# # 复制配置文件
# COPY dnscrypt-proxy.toml /etc/dnscrypt-proxy/dnscrypt-proxy.toml
# # 设置权限
# RUN chmod 644 /etc/dnscrypt-proxy/dnscrypt-proxy.toml
# # 仅暴露需要的端口
# EXPOSE 53/tcp 53/udp
# ENTRYPOINT ["dnscrypt-proxy", "--config", "/etc/dnscrypt-proxy/dnscrypt-proxy.toml"]

# Docker 官方推荐遵循下面这条原则：ENTRYPOINT 定义"执行什么程序"，CMD 定义"默认参数"。
ENTRYPOINT ["dnscrypt-proxy"]
CMD ["--config", "/etc/dnscrypt-proxy/dnscrypt-proxy.toml"]