#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apk update -q
apk add --no-cache -q \
    ca-certificates \
    samba \
    samba-client \
    samba-client-libs \
    samba-common \
    samba-common-server-libs \
    samba-common-tools \
    # samba-dc \
    # samba-dc-libs \
    # samba-dev \
    # samba-doc \
    # samba-libnss-winbind \
    samba-libs \
    # samba-libs-py3 \
    # samba-pidl \
    samba-server \
    samba-server-libs \
    # samba-server-openrc \
    # samba-test \
    samba-util-libs
    # samba-winbind \
    # samba-winbind-clients \
    # samba-winbind-krb5-locator \

# Version 4.20.6
version=$(smbd --version)
version=$(echo "$version" | awk '/Version/ {print $2}')
echo "version=${version}"
