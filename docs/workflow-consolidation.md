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

## Stage 2 — main workflow inventory and retirement gates (2026-10-16)

Baseline: `main@c882d6921ae830bed3cebbb9f6a5aab437210548`. This stage is a read-only YAML audit recorded here, not authorization to delete protected workflows or alter production publication.

- **16** workflow YAML files, **8632** source lines (approximately **334.3 KiB**).
- The three largest: `docker_allinone_gpt.yml` (2,042 lines), `docker_allinone_dev.yml` (1,446), and `docker_allinone.yml` (1,331). They account for **55.8%** of all workflow lines; reducing count alone will not remove most duplicated logic.
- README JSON schema v2 remains the single source for 24 applications and 30 targets. Neither Markdown-only lab nor generated application summary is a production configuration source.

### Verified internal reusable-workflow edges

```text
docker_allinone.yml --------+
                            +--> callable-fetch-app-version.yml
monitor-images.yml ---------+

call-build_dev.yml ------------> build-docker_indocker.yml
image-pipeline.yml ------------> build-docker.yml (dry-run and publish branches)
call-fetch_dev.yml ------------> callable-fetch-layers.yml
```

Do not remove a callee while one of these caller edges remains. External `repository_dispatch`, manual automation, and downstream reusable-workflow consumers are not established by an internal source audit.

### Workflows to preserve during incremental migration

| Class | Workflows | Reason |
|---|---|---|
| Production | `docker_allinone.yml` | Only intended authoritative build/publish entry; keep its existing triggers and tags |
| Independent monitor | `monitor-images.yml` | Separate successful monitoring path; its daily schedule overlaps production at 01:00 UTC but must not be retired before tested parity |
| Test and research | `docker_allinone_gpt.yml`, `docker_allinone_dev.yml` | Retain guarded smoke/comparison and promotion research, particularly non-publishing checks |
| Compatibility matrix | `call-build_dev.yml` | Current caller of containerized builder; explicitly protected migration anchor |
| Standalone utilities | `pull_artifact-dev.yml`, `download_artifact.yml` | Independent user workflows; not building-block deletion candidates |

### Nine other workflows and first-pass disposition

| Workflow | Internal caller | Disposition before approval for retirement |
|---|---|---|
| `callable-fetch-app-version.yml` | Production and independent monitor | **Keep**; shared metadata probe |
| `build-docker_indocker.yml` | `call-build_dev.yml` | **Keep** until container-build compatibility migration and smoke validation |
| `build-docker.yml` | `image-pipeline.yml` | **Keep** until dry-run/publish behavior is absorbed and tested |
| `callable-fetch-layers.yml` | `call-fetch_dev.yml` | **Keep**; shared OCI layer collector |
| `call-fetch_dev.yml` | No internal caller (manual entry) | Candidate for merger with other layer diagnostics after artifact schema comparison |
| `call-fetch_stable.yml` | No internal caller (manual entry) | Candidate for layer-diagnostics consolidation; verify its multi-arch output contract first |
| `baseimage_dev.yml` | No internal caller (manual and events) | Candidate for consolidated base-image inspection; verify runtime/matrix/outputs first |
| `meta-app_dev.yml` | No internal caller (manual entry) | Candidate to thin into a wrapper around the existing metadata probe, keeping troubleshooting semantics |
| `image-pipeline.yml` | No internal caller (manual entry) | Candidate to absorb into `docker_allinone_dev.yml` before retiring its dependent `build-docker.yml` |

### Implementation order and acceptance criteria

1. **No-publication parity:** compare outputs of layer inspectors and metadata probes on fixed immutable image digests; record platform, output JSON, Artifact names, and exit status. Do not delete originals first.
2. **Thin diagnostic entry points:** consolidate `baseimage_dev.yml`, `call-fetch_stable.yml`, and `meta-app_dev.yml` only when equivalent on-demand functionality has a verified replacement. Retain `call-fetch_dev.yml` and `callable-fetch-layers.yml` until that comparison is complete.
3. **Experimental build migration:** bring the useful `image-pipeline.yml` dry-run/matrix behavior into `docker_allinone_dev.yml`; ensure publishing remains off by default. Only then consider removing `image-pipeline.yml` and `build-docker.yml`.
4. **Containerized compatibility:** preserve `call-build_dev.yml` until `build-docker_indocker.yml` behavior has been validated or intentionally superseded; do not silently abandon `workflow_call` clients.
5. **Production and monitoring:** after full check → build → test → publish validation, evaluate sharing version probe code and daily monitoring runs. Keep the two existing schedules until explicit validation and approval to merge.
6. **Cleanup gate:** run GitHub Actions YAML validation, scan every internal `uses: ./.github/workflows/...` reference, compare current 24-app/30-target matrix, and inspect non-publishing Actions results before an individual workflow is retired. No forced pushes or registry tag changes.

Stage-2 inventory itself changes **documentation only**; zero workflows removed or modified at this audit checkpoint.



### Stage 2 integration checkpoint — shared production dispatcher

`docker_allinone.yml` now presents `execution_route: production|dev` on manual dispatch. `production` is the unchanged default for cron/repository dispatch, and the existing `prepare` job is skipped on Dev-only manual invocations. `dev` calls `.github/workflows/docker_allinone_dev.yml` through `workflow_call`, preserving `auto`, `build`, and dedicated promotion modes, including optional `target_id` and promotion version/revision inputs. The Dev YAML remains independently manually dispatchable until this wrapper path is actually tested. No production image publishing was initiated by this change; GitHub Actions syntax validation and static routing tests do not prove a live Dev promotion.


## Stage 2 completed non-production layer consolidation (2026-10-16)

The new `diagnostics.yml` is the single manual diagnostics entry for app-version probes and OCI layer inspection. Internally it reuses `callable-fetch-app-version.yml` and `callable-fetch-layers.yml`. The `platform-details` matrix preserves the historical `layers-<image>-<arch>/layers.json` and `layer-info-<image>-<arch>/image_*.json` artifact schemas. A new `collect` job uploads `diagnostics-layer-summary` containing `base_layers.json` and `aggregated_layers.json`.

Verified on `main` before retirement:
- `38868334453`: version + per-image layer artifacts, including explicit contract check — success.
- `38868702585`, `38868775865`: per-arch raw inspect and layers compatibility artifacts — success.
- `38869143288`: all five selected images × amd64/arm64 detailed probes; 26 Artifacts, full compatibility validation — success.
- `38869288771`: layer aggregation and final artifact contract — success.
- `38869062943`: Production All-in-One -> reusable Dev preflight, no monitor/build/publish in Dev route — success.

With those tests successful, retire `baseimage_dev.yml`, `call-fetch_stable.yml`, and `call-fetch_dev.yml`. `callable-fetch-layers.yml` stays as an internal callee. Legacy `repository_dispatch` consumers of the deleted files were not discoverable in the repository; external clients must use `diagnostics.yml` manual dispatch. The old `baseimage_dev.yml` path-scoped pull-request trigger was not carried over automatically. `meta-app_dev.yml` remains until its all-platform probing behavior is reviewed; the canonical version probe currently uses a preferred platform. Legacy Docker/GHCR promotion remains separately implemented in Dev and must not be deleted until real publishing parity is tested.

### Post-retirement live verification / 实际验收

- Three superseded YAML entries removed on `main@ded3cba2`: `baseimage_dev.yml`, `call-fetch_stable.yml`, `call-fetch_dev.yml`. This reduces the workflow **entry count 16 -> 14** after adding `diagnostics.yml`.
- Version: `diagnostics.yml` delegates to `callable-fetch-app-version.yml` (non-publishing `vlmcsd` run verified).
- Layers: `diagnostics.yml` delegates to `callable-fetch-layers.yml`, and runs a per-architecture Skopeo compatibility matrix producing the former artifact structures; the new aggregator emits `diagnostics-layer-summary`.
- Real runs: `38869143288` validated 5 images × 2 architectures; `38869288771` validated aggregation; `38869484554` passed 24 configuration tests, 5 table-lab tests, 2 aggregator tests and a 14-workflow dependency guard.
- Production/Dev routing: `38869062943` invoked `docker_allinone.yml` as a reusable workflow in Dev preflight mode. Dev ran only read-only checks and all production publishing jobs were skipped.
- **Not yet proven:** real Dev build/GHCR promotion, end-to-end production publication, legacy meta-app all-platform equivalent behavior. `docker_allinone_dev.yml` and `meta-app_dev.yml` must remain until these are validated.

Removed workflow names must not be silently referenced by external automation. The replacement `diagnostics.yml` exposes a manual profile (`stable` five images / `base` three images), optional single-image override, and version probe inputs.

**Safe Dev default correction.** `execution_route=dev` now defaults to `dev_mode=preflight`; users must explicitly select `auto`, `build`, or a `promote-*` mode. Code review confirms Dev `auto`/`build` can create GitHub Releases and push Docker Hub/GHCR tags when a candidate needs promotion. Neither is a dry-run mode. Do not use these modes for nonpublishing integration tests. The existing GPT nested `preflight` test remains the only verified production-to-Dev execution route.
