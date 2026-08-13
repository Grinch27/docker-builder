ARG base_image=debian:testing-slim
FROM ${base_image}

RUN set -eux; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update -qq; \
    apt-get install --no-install-recommends --no-install-suggests -y -qq \
        ca-certificates \
        curl; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/* /var/log/*.log

CMD ["curl", "--version"]
