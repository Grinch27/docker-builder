#!/usr/bin/env bash
# Requirements: publish the accepted amd64/arm64 archives for adguardvpn-cli:release.
# Unknowns/research: Docker Hub credentials and tag policy are verified on the hosted Runner.
# Optimization: copy both platform manifests under one index without intermediate public tags.
# Risks/verification: reject mixed versions, use the current main SHA, and read back Docker Hub.
set -euo pipefail

artifact_dir=$1
metadata_dir="$artifact_dir/metadata"
target=docker.io/grinch27/adguardvpn-cli:release
regctl="$RUNNER_TEMP/regctl"
work_dir=$(mktemp -d "$RUNNER_TEMP/adguardvpn-publish.XXXXXX")
trap 'rm -rf -- "$work_dir"' EXIT
export REGCTL_CONFIG="$work_dir/registry.json"
layout="ocidir://$work_dir/layout"

version=$(jq -er '
  select(.app == "adguardvpn-cli" and .tag == "release")
  | .platforms
  | select((map(.platform) | sort) == ["linux/amd64", "linux/arm64"])
  | map(.version) | unique | select(length == 1) | .[0] | strings | select(length > 0)
' "$metadata_dir/meta-app.json")

for arch in amd64 arm64; do
  platform="linux/$arch"
  evidence="$metadata_dir/linux_$arch"
  jq -e --arg sha "$GITHUB_SHA" --arg platform "$platform" '
    .sha == $sha and .app == "adguardvpn-cli" and .tag == "release" and
    .platform == $platform and .phase == "complete" and .exit_code == 0
  ' "$evidence/result.json" >/dev/null
  jq -e --arg version "$version" '
    .test_result == "success" and .actual_version == $version
  ' "$evidence/snapshot.json" >/dev/null

  archive_files=$(jq -er --arg platform "$platform" '
    [.archives[] | select(.platform == $platform)]
    | select(length == 1) | .[0].files | select(length > 0)[]
  ' "$metadata_dir/metadata_sum.json")
  mapfile -t files <<< "$archive_files"
  for index in "${!files[@]}"; do
    files[$index]="$artifact_dir/output/${files[$index]}"
  done
  cat -- "${files[@]}" | xz --decompress --stdout > "$work_dir/$arch.tar"
  "$regctl" image import "$layout:$arch" "$work_dir/$arch.tar"
  rm -- "$work_dir/$arch.tar"
done

"$regctl" index create "$layout:release" --ref "$layout:amd64" --ref "$layout:arm64" >/dev/null

index_platforms() {
  "$regctl" manifest get "$1" --format raw-body | jq -ce '
    [.manifests[] | {os: .platform.os, arch: .platform.architecture, digest}]
    | sort_by(.arch)
    | select((map(.os + "/" + .arch)) == ["linux/amd64", "linux/arm64"])
  '
}

verify_versions() {
  local ref=$1 arch
  for arch in amd64 arm64; do
    "$regctl" image config --platform "linux/$arch" "$ref" --format raw-body |
      jq -e --arg arch "$arch" --arg version "$version" '
        .os == "linux" and .architecture == $arch and .config.Labels.version == $version
      ' >/dev/null
  done
}

expected_index=$(index_platforms "$layout:release")
verify_versions "$layout:release"

remote_sha=$(git ls-remote --exit-code origin refs/heads/main | cut -f1)
if [[ "$remote_sha" != "$GITHUB_SHA" ]]; then
  echo "::notice::main advanced to $remote_sha. Skipping publication from $GITHUB_SHA."
  exit 0
fi

if [[ -z "${DOCKER_USERNAME:-}" || -z "${DOCKER_PASSWORD:-}" ]]; then
  echo '::error::Set the DOCKER_USERNAME and DOCKER_PASSWORD Actions secrets for Docker Hub.'
  exit 1
fi
umask 077
printf '%s\n' "$DOCKER_PASSWORD" |
  "$regctl" registry login docker.io --user "$DOCKER_USERNAME" --pass-stdin
unset DOCKER_USERNAME DOCKER_PASSWORD

"$regctl" image copy "$layout:release" "$target"
observed_index=$(index_platforms "$target")
if [[ "$observed_index" != "$expected_index" ]]; then
  echo '::error::Docker Hub platform manifests differ from the accepted archives.'
  exit 1
fi
verify_versions "$target"
digest=$("$regctl" manifest head "$target" --require-list)
printf 'Published %s version=%s platforms=linux/amd64,linux/arm64 %s\n' \
  "$target" "$version" "$digest" | tee -a "$GITHUB_STEP_SUMMARY"
