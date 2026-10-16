#!/usr/bin/env bash
# Universal Buildx builder for all application build directories.
set -euo pipefail
: "${arch_branch:?missing arch_branch}"
: "${repo_dockerhub:?missing repo_dockerhub}"
: "${base_image:?missing base_image}"
: "${tag_repo:?missing tag_repo}"
: "${registry_local:?missing registry_local}"
: "${version:?missing version}"
dockerfile="${dockerfile:-Dockerfile}"
[[ "${dockerfile}" =~ ^[a-zA-Z0-9_.-]+$ ]] || { echo "Unsafe Dockerfile name" >&2; exit 2; }
mapfile -t candidates < <(find . -maxdepth 1 -type f -iname "${dockerfile}" -print)
[[ "${#candidates[@]}" -eq 1 ]] || { echo "Expected one Dockerfile: ${dockerfile}" >&2; exit 2; }
args=(
  docker buildx build
  --platform "${arch_branch}"
  --file "${candidates[0]}"
  --tag "${registry_local}/${repo_dockerhub}:${tag_repo}"
  --build-arg "base_image=${base_image}"
  --label "version=${version}"
  --output "type=registry,registry.insecure=true"
)
if [[ -n "${build_arg:-}" ]]; then
  args+=(--build-arg "build_arg=${build_arg}")
fi
"${args[@]}" .
