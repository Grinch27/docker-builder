ARG base_image=alpine:latest
FROM ${base_image}

RUN set -x \
    # ===== apk dependencies =====
    && apk update \
    && apk add --no-cache \
        ca-certificates \
        privoxy \
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
