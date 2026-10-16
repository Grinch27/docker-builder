#!/usr/bin/env bash
# Shared Buildx invocation: registry (production default) or load (isolated smoke).
set -euo pipefail
: "${arch_branch:?missing arch_branch}"
: "${base_image:?missing base_image}"
dockerfile="${dockerfile:-Dockerfile}"
[[ "${dockerfile}" =~ ^[a-zA-Z0-9_.-]+$ ]] || { echo "Unsafe Dockerfile name" >&2; exit 2; }
mapfile -t candidates < <(find . -maxdepth 1 -type f -iname "${dockerfile}" -print)
[[ "${#candidates[@]}" -eq 1 ]] || { echo "Expected one Dockerfile: ${dockerfile}" >&2; exit 2; }

args=(docker buildx build --platform "${arch_branch}" --file "${candidates[0]}")
case "${build_output:-registry}" in
  registry)
    : "${repo_dockerhub:?missing repo_dockerhub}"
    : "${tag_repo:?missing tag_repo}"
    : "${registry_local:?missing registry_local}"
    : "${version:?missing version}"
    args+=(--tag "${registry_local}/${repo_dockerhub}:${tag_repo}"
           --build-arg "base_image=${base_image}"
           --label "version=${version}"
           --output "type=registry,registry.insecure=true")
    ;;
  load)
    : "${image_ref:?missing image_ref}"
    args+=(--tag "${image_ref}" --build-arg "base_image=${base_image}" --load)
    ;;
  *)
    echo "Unknown build_output: ${build_output}" >&2
    exit 2
    ;;
esac
if [[ -n "${build_arg:-}" ]]; then
  args+=(--build-arg "build_arg=${build_arg}")
fi
"${args[@]}" .
