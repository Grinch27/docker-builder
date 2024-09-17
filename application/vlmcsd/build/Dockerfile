ARG base_image=alpine:latest
FROM ${base_image} as patcher
RUN set -x \
    && cat << 'EOF' > /fix-dangling-pointer.patch
--- a/src/kms.c
+++ b/src/kms.c
@@ -467,1 +467,1 @@ const char* pid;
+   char ePid[PID_BUFFER_SIZE];
    if (KmsResponseParameters[index].Epid == NULL)
    {
#ifndef NO_RANDOM_EPID
        if (RandomizationLevel == 2)
        {
-            char ePid[PID_BUFFER_SIZE];
            generateRandomPid(index, ePid, Lcid, HostBuild);
            pid = ePid;
        }
EOF



ARG base_image=alpine:latest
FROM ${base_image} as builder
ARG PATCH_FILE_ABS_PATH=/fix-dangling-pointer.patch
COPY --from=patcher ${PATCH_FILE_ABS_PATH} ${PATCH_FILE_ABS_PATH}

WORKDIR /root
RUN set -x \
    && apk update \
    && apk add --no-cache \
        build-base \
        git \
        make \
    && git clone --branch master --single-branch https://github.com/Wind4/vlmcsd.git \
    && cd vlmcsd/ \
    && patch -p1 < ${PATCH_FILE_ABS_PATH} \
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
