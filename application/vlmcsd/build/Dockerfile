ARG base_image=alpine:latest
FROM ${base_image} as builder
WORKDIR /root
RUN set -x \
    && apk update \
    && apk add --no-cache \
        build-base \
        git \
        make \
    && git clone --branch master --single-branch https://github.com/Wind4/vlmcsd.git \
    && cd vlmcsd/ \
    && make

ARG base_image=alpine:latest
FROM ${base_image}
# WORKDIR /root/
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

# CMD [ "/usr/bin/vlmcsd", "-D", "-d" ]
ENTRYPOINT ["/docker-entrypoint.sh"]
