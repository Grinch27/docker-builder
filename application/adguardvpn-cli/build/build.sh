#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

# 搜索 Dockerfile 文件，不区分大小写
dockerfile=$(find "${dir_current}" -type f -iname 'dockerfile')
if [ -z "$dockerfile" ]; then
  echo "未找到 Dockerfile 文件"
else
  echo "找到 Dockerfile 文件: ${dockerfile}"
fi

# docker buildx
docker buildx build \
    --platform ${arch_branch} \
    --file ${dockerfile} \
    --tag "${registry_local}/${repo_dockerhub}:${tag_repo}" \
    --build-arg base_image=${base_image} \
    --build-arg update_channel=${update_channel} \
    --label version=${version} \
    --output type=registry,registry.insecure=true \
    .
# --output type=tar,dest=${output_tar} \

# variant=""
# if echo "${arch}" | grep -q "arm/v"; then
#   variant=$(echo ${arch} | cut -d'/' -f2)
#   arch=$(echo ${arch} | cut -d'/' -f1)
# fi

# data_json=$(skopeo inspect \
#   --override-os=${os} \
#   --override-arch=${arch} \
#   ${variant:+--override-variant=${variant}} \
#   --format=json \
#   docker://docker.io/${repo} | jq .)