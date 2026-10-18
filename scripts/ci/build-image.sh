#!/usr/bin/env bash
# Requirements: execute from application root; only the exact configured build Tag selects a Dockerfile.
# Unknowns/research: public publication is outside the nonpublishing migration acceptance.
# Optimization: one Buildx invocation exports all configured platforms to the local registry.
# Risks/verification: no shared/case-insensitive fallback; test missing files, overrides and full Buildx argv.
set -euo pipefail
: "${arch_branch:?missing arch_branch}"
: "${base_image:?missing base_image}"
build_tag="${build_tag-${tag_repo-latest}}"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
expected=$(python3 - "$script_dir" "$(basename -- "$PWD")" "$build_tag" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
from catalog import dockerfile_name
print(dockerfile_name(sys.argv[2], sys.argv[3]))
PY
)
[[ ! ${dockerfile+x} || "$dockerfile" == "$expected" ]] || { echo "Dockerfile override forbidden for $build_tag: expected $expected" >&2; exit 2; }
dockerfile="$expected"
[[ -f "$dockerfile" && ! -L "$dockerfile" ]] || { echo "Missing independent Dockerfile for $build_tag: $PWD/$dockerfile" >&2; exit 2; }

args=(docker buildx build --platform "${arch_branch}" --file "$dockerfile")
: "${repo_dockerhub:?missing repo_dockerhub}"
: "${tag_repo:?missing tag_repo}"
: "${registry_local:?missing registry_local}"
: "${version:?missing version}"
[[ "$registry_local" == '127.0.0.1:5000' ]] || { echo 'Only the local acceptance registry is allowed' >&2; exit 2; }
args+=(--tag "${registry_local}/${repo_dockerhub}:${tag_repo}"
       --build-arg "base_image=${base_image}"
       --label "version=${version}"
       --output "type=registry,registry.insecure=true")
if [[ -n "${build_arg:-}" ]]; then
  args+=(--build-arg "build_arg=${build_arg}")
fi
"${args[@]}" .
