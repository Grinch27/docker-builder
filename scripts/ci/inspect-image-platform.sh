#!/usr/bin/env bash
# Platform-specific compat outputs for stable fetch and baseimage diagnostics.
# Writes to $RUNNER_TEMP/diagnostics and emits safe artifact filenames.
set -euo pipefail
image="${1:?image required}"
arch="${2:?architecture required}"
case "${arch}" in amd64|arm64) ;; *) echo "Unsupported architecture: ${arch}" >&2; exit 2 ;; esac
[[ "${image}" =~ ^[a-zA-Z0-9][a-zA-Z0-9._/:@-]*$ ]] || { echo "Invalid image name" >&2; exit 2; }
out="${RUNNER_TEMP:?}/diagnostics"
mkdir -p "${out}"
base_name="${image//:/-}"
base_name="${base_name//\//_}"
stable_name="${image//:/_}"
stable_name="${stable_name//\//_}"
raw="${out}/inspect.json"
skopeo inspect --override-os=linux --override-arch="${arch}" --format=json "docker://docker.io/${image}" > "${raw}"
jq -e '.Layers | type == "array" and length > 0' "${raw}" >/dev/null
jq '.Layers' "${raw}" > "${out}/layers.json"
jq -c --arg image "${image}" --arg arch "${arch}" '{image:$image,architecture:$arch,raw_data:.}' "${raw}" > "${out}/image_${base_name}_${arch}.json"
echo "base_name=${base_name}" >> "${GITHUB_OUTPUT:?}"
echo "stable_name=${stable_name}" >> "${GITHUB_OUTPUT}"
echo "Compatibility inspect: ${image} linux/${arch}"
