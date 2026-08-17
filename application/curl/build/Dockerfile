ARG base_image=alpine:edge
FROM ${base_image}

RUN set -eux \
    # ===== apk dependencies =====
    && apk update \
    && apk add --no-cache \
        ca-certificates \
        curl \
    # ===== Clean apk =====
    && rm -rf /var/cache/apk/* \
    && rm -rf /var/log/*.log

# ENTRYPOINT []

CMD ["/bin/sh", "-c", \
    "set -eux; \
    uname -a; \
    curl --version; \
    exec sleep infinity"]