ARG base_image=alpine:latest
FROM ${base_image}

RUN set -x \
    # ===== apk dependencies =====
    && apk update \
    && apk add --no-cache \
        ca-certificates \
        samba \
        samba-client \
        samba-libs \
        samba-server \
        samba-util-libs \
        # ----- full list -----
        # ca-certificates \
        # samba \
        # samba-client \
        # samba-client-libs \
        # samba-common \
        # samba-common-server-libs \
        # samba-common-tools \
        # # samba-dc \
        # # samba-dc-libs \
        # # samba-dev \
        # # samba-doc \
        # # samba-libnss-winbind \
        # samba-libs \
        # # samba-libs-py3 \
        # # samba-pidl \
        # samba-server \
        # samba-server-libs \
        # # samba-server-openrc \
        # # samba-test \
        # samba-util-libs \
        # # samba-winbind \
        # # samba-winbind-clients \
        # # samba-winbind-krb5-locator \
    # ===== Clean apk =====
    && rm -rf /var/cache/apk/* \
    && rm -rf /var/log/*.log \
    # ===== samba configuration =====
    # && echo -e "password\npassword" | smbpasswd -a root \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env sh" >> ${sh_entrypoint} \
    # ----- start samba -----
	&& sh_samba="/start-samba.sh" \
	&& echo "smbd" >> ${sh_samba} \
	&& chmod +x ${sh_samba} \
	&& echo "${sh_samba} &" >> ${sh_entrypoint} \
    # ----- end of docker-entrypoint.sh -----
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

ENTRYPOINT ["/docker-entrypoint.sh"]
