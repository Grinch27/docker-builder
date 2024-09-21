#!/bin/sh

set -x

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

# 搜索 Dockerfile 文件，不区分大小写
dockerfile=$(find "${dir_current}" -type f -iname 'dockerfile')
if [ -z "$dockerfile" ]; then
  echo "未找到 Dockerfile 文件"
  exit 1
else
  echo "找到 Dockerfile 文件: ${dockerfile}"
fi

# ===== docker buildx =====
docker buildx build \
  --platform ${arch_branch} \
  --file ${dockerfile} \
  --tag "${registry_local}/${repo_dockerhub}:${tag_repo}" \
  --build-arg base_image=${base_image} \
  ${build_arg:+--build-arg build_arg=${build_arg}} \
  --label version=${version} \
  --output type=registry,registry.insecure=true \
  .
