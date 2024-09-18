#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

# 检查环境变量 dockerfile 是否已被定义
if [ -z "$dockerfile" ]; then
  dockerfile="Dockerfile"
  echo "环境变量 dockerfile 未定义，使用默认值: ${dockerfile}"
else
  echo "环境变量 dockerfile 已定义: ${dockerfile}"
fi

# 当前目录下搜索 Dockerfile 文件，不区分大小写
dockerfile=$(find "${dir_current}" -type f -iname "${dockerfile}")
if [ -z "$dockerfile" ]; then
  echo "未找到Dockerfile文件 ${dockerfile}"
  exit 1
else
  echo "找到Dockerfile文件 ${dockerfile}"
fi

# docker buildx
docker buildx build \
    --platform ${arch_branch} \
    --file ${dockerfile} \
    --tag "${registry_local}/${repo_dockerhub}:${tag_repo}" \
    --build-arg base_image=${base_image} \
    --label version=${version} \
    --output type=registry,registry.insecure=true \
    .
# --output type=tar,dest=${output_tar} \
