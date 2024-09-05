ARG base_image=alpine:latest
FROM ${base_image}

RUN apk update \
    && apk add --no-cache \
        ca-certificates \
        # curl \
        # tar \
        # gpg \
        squid \
    # clean
    # && apk del --no-cache \
    #     curl \
    #     tar \
    #     gpg \
    && rm -rf /var/cache/apk/* \
    && rm -rf /var/log/*.log

ENTRYPOINT ["sh", "-c", "uname -a && sleep infinity"]
