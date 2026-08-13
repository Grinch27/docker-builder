#!/bin/sh

dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"
echo "tag_version=${tag_version}"
