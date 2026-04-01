#!/bin/sh

set -eux

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

: "${dockerfile:=Dockerfile}"
: "${registry_local:=localhost:5000}"
: "${tag_repo:=latest}"
: "${version:=0.0.0}"
: "${arch_branch:=linux/amd64}"
: "${repo_dockerhub:=grinch27/sdnext}"
: "${base_image:=rocm/dev-ubuntu-24.04}"

# Use case-insensitive exact filename matching and take the first hit.
resolved_dockerfile=$(find "${dir_current}" -type f -iname "${dockerfile}" | head -n 1)
if [ -z "${resolved_dockerfile}" ]; then
  echo "未找到 Dockerfile 文件: ${dockerfile}"
  exit 1
fi
echo "找到 Dockerfile 文件: ${resolved_dockerfile}"

# ===== docker buildx =====
docker buildx build \
  --platform "${arch_branch}" \
  --file "${resolved_dockerfile}" \
  --tag "${registry_local}/${repo_dockerhub}:${tag_repo}" \
  --build-arg "base_image=${base_image}" \
  ${build_arg:+--build-arg build_arg=${build_arg}} \
  --label "version=${version}" \
  --output type=registry,registry.insecure=true \
  .
