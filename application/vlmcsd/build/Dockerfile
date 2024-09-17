ARG base_image=alpine:latest
FROM ${base_image} as builder
RUN set -x \
    && apk update \
    && apk add --no-cache \
        build-base \
        ca-certificates \
        curl \
        git \
        make \
    # ===== Clone source =====
    && repo_dir="/vlmcsd" \
    && git clone https://github.com/Wind4/vlmcsd.git ${repo_dir} --branch=master --single-branch \
    && cd ${repo_dir} \
    # ----- Following fixes https://github.com/Wind4/vlmcsd/issues/90 -----
    && PATCH_TARGET="src/kms.c" \
    && sed -i '467s/const char\* pid;/& char ePid[PID_BUFFER_SIZE];/' ${PATCH_TARGET} \
    && sed -i '473{/char ePid\[PID_BUFFER_SIZE\];/d}' ${PATCH_TARGET} \
    # && cat ${PATCH_TARGET} \
    # ----- make -----
    && make



ARG base_image=alpine:latest
FROM ${base_image}
COPY --from=builder /vlmcsd/bin/vlmcsd /usr/bin/vlmcsd
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
