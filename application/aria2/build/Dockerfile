ARG base_image=alpine:latest
FROM ${base_image}

RUN set -x \
    # ===== apk dependencies =====
    && apk update \
    && apk add --no-cache \
        ca-certificates \
        aria2 \
    # ===== Clean apk =====
    && rm -rf /var/cache/apk/* \
    && rm -rf /var/log/*.log \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env sh" >> ${sh_entrypoint} \
    # ----- start aria2 -----
	&& sh_aria2="/start-aria2.sh" \
	&& echo "aria2c --enable-rpc --rpc-listen-port=6800 --rpc-secret=password" >> ${sh_aria2} \
	&& chmod +x ${sh_aria2} \
	&& echo "${sh_aria2} &" >> ${sh_entrypoint} \
    # ----- end of docker-entrypoint.sh -----
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

ENTRYPOINT ["/docker-entrypoint.sh"]
