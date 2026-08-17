ARG base_image=alpine:edge
FROM ${base_image}

RUN set -eux; \
    apk add --no-cache \
        ca-certificates \
        curl

CMD ["curl", "--version"]
