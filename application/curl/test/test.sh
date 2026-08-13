#!/bin/sh

dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

version=$(curl --version | awk 'NR==1 {print $2}')
echo "version=${version}"
