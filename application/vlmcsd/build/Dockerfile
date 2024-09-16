FROM alpine:latest as builder
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

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /root/vlmcsd/bin/vlmcsd /usr/bin/vlmcsd
EXPOSE 1688/tcp
CMD [ "/usr/bin/vlmcsd", "-D", "-d" ]
