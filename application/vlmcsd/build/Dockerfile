ARG base_image=alpine:latest
FROM ${base_image} as builder
WORKDIR /root
RUN set -x \
    && apk update \
    && apk add --no-cache \
        build-base \
        ca-certificates \
        curl \
        git \
        make \
    && git clone https://github.com/Wind4/vlmcsd.git --branch=master --single-branch \
    && cd vlmcsd/ \
    # ----- fix-dangling-pointer.patch -----
    && PATCH_URL="https://raw.githubusercontent.com/Grinch27/docker-builder/main/application/vlmcsd/build/fix-dangling-pointer.patch" \
    && PATCH_FILE="/tmp/fix-dangling-pointer.patch" \
    && PATCH_TARGET="src/kms.c" \
    && curl -fsSL ${PATCH_URL} -o ${PATCH_FILE} \
    && patch -p1 < ${PATCH_FILE} \
    && cat ${PATCH_TARGET} \
    # ----- make -----
    && make



ARG base_image=alpine:latest
FROM ${base_image}
COPY --from=builder /root/vlmcsd/bin/vlmcsd /usr/bin/vlmcsd
RUN set -x \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env sh" >> ${sh_entrypoint} \
    # ----- sh: /bin/app -----
    && sh_vlmcsd="/start-vlmcsd.sh" \
	&& echo 'vlmcsd -D -d' >> ${sh_vlmcsd} \
	&& chmod +x ${sh_vlmcsd} \
	&& echo "${sh_vlmcsd} &" >> ${sh_entrypoint} \
    # ----- end of docker-entrypoint.sh -----
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

EXPOSE 1688/tcp
# WORKDIR /root/
# CMD [ "/usr/bin/vlmcsd", "-D", "-d" ]
ENTRYPOINT ["/docker-entrypoint.sh"]
