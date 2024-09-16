ARG base_image=alpine:latest
FROM ${base_image}

ARG update_channel=release
ENV update_channel=${update_channel}

RUN set -x \
    # ===== apk dependencies =====
    && apk update \
    && apk add --no-cache \
        ca-certificates \
        curl \
        tar \
        gpg \
    # ===== Setup AdGuardVPNCLI =====
    && URL_SH="https://raw.githubusercontent.com/AdguardTeam/AdGuardVPNCLI/master/scripts/${update_channel}/install.sh" \
    && FILE_SH="/install.sh" \
    && curl -fsSL ${URL_SH} -o ${FILE_SH} \
    && sed -i 's/read -r response < \/dev\/tty/response="y"/g' ${FILE_SH} \
    && chmod +x ${FILE_SH} \
    && sh --verbose ${FILE_SH} \
    && rm -f ${FILE_SH} \
    # ===== Clean pre-install =====
    && apk del --no-cache \
        curl \
        tar \
        gpg \
    # ===== Clean apk =====
    && rm -rf /var/cache/apk/* \
    && rm -rf /var/log/*.log \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env sh" >> ${sh_entrypoint} \
    # ----- end of docker-entrypoint.sh -----
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

ENTRYPOINT ["/docker-entrypoint.sh"]
