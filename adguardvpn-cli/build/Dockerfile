ARG base_image=alpine:latest
FROM ${base_image}

ARG update_channel=release
ENV update_channel=${update_channel}

RUN apk update \
    && apk add --no-cache \
        ca-certificates \
        curl \
        tar \
        gpg \
    # install.sh
    && URL_SH="https://raw.githubusercontent.com/AdguardTeam/AdGuardVPNCLI/master/scripts/${update_channel}/install.sh" \
    && FILE_SH="/install.sh" \
    && curl -fsSL ${URL_SH} -o ${FILE_SH} \
    && sed -i 's/read -r response < \/dev\/tty/response="y"/g' ${FILE_SH} \
    && chmod +x ${FILE_SH} \
    && sh --verbose ${FILE_SH} \
    && rm -f ${FILE_SH} \
    # clean
    && apk del --no-cache \
        curl \
        tar \
        gpg \
    && rm -rf /var/cache/apk/* \
    && rm -rf /var/log/*.log

ENTRYPOINT ["sh", "-c", "uname -a && sleep infinity"]
