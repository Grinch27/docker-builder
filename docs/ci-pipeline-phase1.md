# CI Pipeline Phase 1

This note documents the phase 1 split of monitor/build/publish responsibilities.

## What Changed

- `monitor-images.yml` is the new daily monitor workflow.
  - It collects app versions.
  - It writes stable monitor artifacts:
    - `build-matrix.json`
    - `monitor-state.json`
    - `monitor-report.md`
    - `versions.json`
  - It updates `README.md` only when semantic image state changes.
  - It does not require Docker Hub write secrets.

- `version-compare-build.yml` is kept as a compatibility workflow.
  - Manual dispatch and repository dispatch remain available.
  - It uses the same stable README renderer.
  - It can still conditionally call `build-docker.yml`.
  - Its daily schedule moved to `monitor-images.yml`.

- `image-pipeline.yml` is the explicit build/publish pipeline.
  - It accepts either a JSON matrix or a single app input.
  - It defaults to `publish=false` for dry runs.
  - It only passes Docker Hub secrets when `publish=true`.

- `build-docker.yml` now has a `publish` input.
  - Default is `true` for compatibility with existing callers.
  - `publish=false` builds, tests, saves, and compresses without Docker Hub push or GitHub Release upload.
  - Docker Hub login moved to the publish step.
  - Image tests now fail the job by default, so publish steps do not run after test failure.

## Stable README Rules

The generated README section no longer contains volatile run metadata:

- No refresh timestamp.
- No per-app `updated_at`.
- No run id, duration, or runner host.

The README version JSON keeps stable keys sorted by `json.dumps(sort_keys=True)`.

## Compatibility

Existing manual build inputs are preserved:

- `app_branch`
- `tag_repo`
- `force_push`
- `custom_env`
- `runner_image`

`build-docker.yml` added `publish`; old callers that omit it keep the previous publish behavior.

Behavior change:

- The old scheduled `version-compare-build.yml` path no longer runs daily.
- Daily monitoring is now `monitor-images.yml`.
- Tests are now a default publish gate.

## Recommended Usage

Daily monitor:

1. Run `monitor-images.yml`.
2. Download `monitor-output`.
3. If `build-matrix.json` has targets, pass it to `image-pipeline.yml`.

Dry run one app:

1. Dispatch `image-pipeline.yml`.
2. Set `app_branch`.
3. Keep `publish=false`.

Publish one app or matrix:

1. Dispatch `image-pipeline.yml`.
2. Provide single app inputs or `build_matrix`.
3. Set `publish=true`.
4. Confirm Docker Hub secrets are configured.

## Follow-Up Decisions

- Decide whether `version-compare-build.yml` should eventually be removed.
- Decide whether `build-docker_indocker.yml` remains supported.
- Decide whether README should be updated only after successful publish rather than after monitor.
- Decide whether publish failures should remain `continue-on-error` or become blocking.
