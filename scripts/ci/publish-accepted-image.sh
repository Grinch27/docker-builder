#!/usr/bin/env bash
# Requirements: publish the exact accepted archives with one Docker Hub index per Target.
# Unknowns/research: confirm hosted Docker Hub access and compressed artifact storage on daily runs.
# Optimization: reuse the verified archives and remove each unpacked tar after importing it.
# Risks/verification: require the same main SHA, accepted metadata and exact remote platform digests.
set -euo pipefail

artifact_dir=$1
metadata_dir="$artifact_dir/metadata"
regctl="$RUNNER_TEMP/regctl"
[[ "$GITHUB_REPOSITORY" == Grinch27/docker-builder &&
   "$GITHUB_REF" == refs/heads/main &&
   "$repo_dockerhub" =~ ^grinch27/[a-z0-9][a-z0-9_.-]*$ &&
   "$publish_tag" =~ ^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$ ]] || {
  echo '::error::Publication requires the official main branch and a configured Docker Hub destination.'
  exit 1
}
target="docker.io/$repo_dockerhub:$publish_tag"
[[ -s "$metadata_dir/acceptance.json" ]] || {
  echo "::error::$app_branch:$tag_repo has no successful Container acceptance in this run."
  exit 1
}
platforms_json=$(jq -cn --arg csv "$arch_branch" '$csv | split(",")')
IFS=',' read -ra platforms <<< "$arch_branch"
version=$(jq -er --arg sha "$GITHUB_SHA" --arg app "$app_branch" --arg tag "$tag_repo" \
  --arg repo "$repo_dockerhub" --arg publish "$publish_tag" --argjson platforms "$platforms_json" '
  select(.sha == $sha and .app_branch == $app and .tag_repo == $tag and
         .repo_dockerhub == $repo and .publish_tag == $publish and .platforms == $platforms)
  | .version | strings | select(length > 0)
' "$metadata_dir/acceptance.json")
jq -e --argjson platforms "$platforms_json" '
  (.archives | map(.platform) | sort) == ($platforms | sort)
' "$metadata_dir/metadata_sum.json" >/dev/null

if [[ -z "${DOCKER_USERNAME:-}" || -z "${DOCKER_PASSWORD:-}" ]]; then
  echo '::error::Set the DOCKER_USERNAME and DOCKER_PASSWORD Actions secrets for Docker Hub.'
  exit 1
fi

umask 077
work_dir=$(mktemp -d "$RUNNER_TEMP/image-publish.XXXXXX")
trap 'rm -rf -- "$work_dir"' EXIT
export REGCTL_CONFIG="$work_dir/registry.json"
layout="ocidir://$work_dir/layout"
refs=()

for platform in "${platforms[@]}"; do
  label=${platform//\//_}
  archive_files=$(jq -er --arg platform "$platform" '
    .archives[] | select(.platform == $platform) |
    .files | select(length > 0)[] |
    select(test("^(file-split/)?[A-Za-z0-9_.-]+\\.tar\\.xz(\\.part[0-9]+)?$"))
  ' "$metadata_dir/metadata_sum.json")
  mapfile -t files <<< "$archive_files"
  for index in "${!files[@]}"; do
    files[$index]="$artifact_dir/output/${files[$index]}"
  done
  cat -- "${files[@]}" | xz --decompress --stdout > "$work_dir/import.tar"
  expected_tar=$(jq -er --arg platform "$platform" '
    .archives[] | select(.platform == $platform) | .sha256 | select(test("^[a-f0-9]{64}$"))
  ' "$metadata_dir/metadata_sum.json")
  printf '%s  %s\n' "$expected_tar" "$work_dir/import.tar" | sha256sum --check --status
  "$regctl" image import "$layout:$label" "$work_dir/import.tar" --name "$repo_dockerhub:$tag_repo"
  rm -- "$work_dir/import.tar"
  refs+=(--ref "$layout:$label")
done

"$regctl" index create "$layout:accepted" "${refs[@]}" >/dev/null

index_platforms() {
  "$regctl" manifest get "$1" --format raw-body | jq -ce --argjson expected "$platforms_json" '
    [.manifests[] | {os: .platform.os, arch: .platform.architecture, variant: (.platform.variant // ""), digest}]
    | sort_by(.os, .arch, .variant)
    | . as $members
    | select(length == ($expected | length) and all($expected[];
        split("/") as $p |
        ([$members[] | select(.os == $p[0] and .arch == $p[1] and
          ($p[2] == null or .variant == $p[2]))] | length) == 1))
  '
}

verify_versions() {
  local ref=$1 platform
  for platform in "${platforms[@]}"; do
    "$regctl" image config --platform "$platform" "$ref" --format raw-body |
      jq -e --arg platform "$platform" --arg version "$version" '
        ($platform | split("/")) as $p |
        .os == $p[0] and .architecture == $p[1] and
        ($p[2] == null or .variant == $p[2]) and .config.Labels.version == $version
      ' >/dev/null
  done
}

expected_index=$(index_platforms "$layout:accepted")
verify_versions "$layout:accepted"

remote_sha=$(git ls-remote --exit-code origin refs/heads/main | cut -f1)
if [[ "$remote_sha" != "$GITHUB_SHA" ]]; then
  echo "::error::main advanced to $remote_sha. Refusing to publish $GITHUB_SHA."
  exit 1
fi

printf '%s\n' "$DOCKER_PASSWORD" |
  "$regctl" registry login docker.io --user "$DOCKER_USERNAME" --pass-stdin
unset DOCKER_USERNAME DOCKER_PASSWORD

"$regctl" image copy "$layout:accepted" "$target"
observed_index=$(index_platforms "$target")
if [[ "$observed_index" != "$expected_index" ]]; then
  echo '::error::Docker Hub platform manifests differ from the accepted archives.'
  exit 1
fi
verify_versions "$target"
digest=$("$regctl" manifest head "$target" --require-list)
printf 'Published %s version=%s platforms=%s %s\n' \
  "$target" "$version" "$arch_branch" "$digest" | tee -a "$GITHUB_STEP_SUMMARY"
