# Docker workflow consolidation — stage 1 (2026-10-15)

## Scope and intent

Use recently exercised GitHub Actions workflows as migration anchors, preserving independent artifact utilities. This stage removes three superseded entry points and stops repeated automatic execution of transitional build workflows. Production build, tag, publish, archive, application and platform logic is intentionally unchanged.

## Protected migration anchors (seven)

| Workflow | Role | Stage-1 behavior |
| --- | --- | --- |
| `docker_allinone.yml` | Production version monitor, check, build and publish | Keep daily schedule; comment-only edit |
| `monitor-images.yml` | Independently successful version monitor | Keep daily schedule, manual trigger and artifact format until separate merge validation |
| `docker_allinone_gpt.yml` | Non-publishing smoke tests | Keep unchanged; its build/promotion job remains gated off |
| `docker_allinone_dev.yml` | Experimental compare and promotion logic | Keep manual and repository dispatch; remove schedule and file-specific push trigger |
| `call-build_dev.yml` | Legacy containerized matrix builder | Keep manual and repository dispatch for migration; remove schedule |
| `pull_artifact-dev.yml` | Pull and export images | Keep as independent utility |
| `download_artifact.yml` | Download, compress and split artifacts | Keep as independent utility |

The two artifact utility workflow files are explicitly protected from retirement or automatic integration into the production builder.

## Retired workflows

| File | Reason and replacement |
| --- | --- |
| `call-build.yml` | Obsolete manually dispatched matrix calling `build-docker.yml`. The production `docker_allinone.yml` contains all 24 explicit app/tag combinations, including the dynamically discovered `curl:latest`; `call-build_dev.yml` remains as a compatibility/testing reference. |
| `matrix.yml` | Separate base-image layer matrix plus build/push pipeline. Its daily/automatic role is superseded by the production All in One prepare/check/build path; it has no internal workflow callers. |
| `version-compare-build.yml` | Duplicate version monitor, README renderer and conditional build coordinator. The production All in One already invokes `scripts/ci/monitor_state.py` and conditionally builds changed targets. |

Removed workflows were not directly referenced by other workflow files at this baseline. External `repository_dispatch` clients are **not** provably absent; any such integrations must migrate to an active entry point.

## Remaining legacy workflows (not deleted)

`baseimage_dev.yml`, `build-docker.yml`, `build-docker_indocker.yml`, `call-fetch_dev.yml`, `call-fetch_stable.yml`, `callable-fetch-app-version.yml`, `callable-fetch-layers.yml`, `image-pipeline.yml` and `meta-app_dev.yml`.

In particular, `monitor-images.yml` still calls `callable-fetch-app-version.yml`, `call-build_dev.yml` still calls `build-docker_indocker.yml`, `image-pipeline.yml` still calls `build-docker.yml`, and `call-fetch_dev.yml` still calls `callable-fetch-layers.yml`. Do not remove those callees before callers are migrated.

## Required behavior and verification

- No change to `application/*`, `vars.env`, Dockerfiles, build/test scripts, base images, platform lists, Docker Hub/GHCR tags or GitHub Release asset format.
- No direct secret changes, image publication or explicit Actions dispatch in this stage.
- Source checks: all seven protected workflow files remain present; both transitional workflows retain `workflow_dispatch` and `repository_dispatch`, but have no `schedule`; production and monitor schedules remain.
- Validate future production and monitor scheduled jobs separately. A successful monitoring run or a production run that skips build jobs does **not** prove the publish path.
- Future integration: migrate the useful dry-run/matrix selection from `image-pipeline.yml`, comparison and promotion decisions from Dev, and isolated smoke/artifact evidence from GPT. Verify production equivalence before retiring their old sources.
- Production failure gates (check status, test outcome, registry push) and cross-registry parity still require follow-up; they were **not** modified by this commit.

Rollback: revert the consolidation commit on `main` to restore the removed YAML entry points and former automatic triggers. Avoid force-pushing branch history.
