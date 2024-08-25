#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apk add --no-cache git make build-base
git clone --branch master --single-branch https://github.com/Wind4/vlmcsd.git
cd vlmcsd/
make

cp bin/vlmcsd /usr/bin/vlmcsd

/usr/bin/vlmcsd -D -d
