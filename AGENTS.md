# AGENTS.md — docker-builder

本文件适用于仓库根目录及所有子目录。以下“当前维护规范”用于实际变更；后面的四份历史文档仅为追溯原始设计与验证过程，**不是当前代码、工作流状态或生产授权的权威来源**。发生差异时，先读取 `main` 当前源码并执行验证。

## 当前维护规范 / Active guidance

### 配置和脚本唯一来源

- `README.md` 中 `app-config` 标记内的 schema-v2 JSON 是应用/构建 Target 配置与 `monitor.records` 的权威记录；`config` 经人工审核，监控工作流只在真实状态变化时更新 `monitor.records`。不要把 Markdown 应用清单当成 JSON 配置来源。
- `README.md` 的 **Applications / 应用清单** 位于文末，`app-summary` 标记内的展示字段由配置和监控记录生成。**Meta-app / Test 两列例外：其中每个应用的完整 Shell 代码是脚本的唯一维护源。** 保留 `app-meta:<app>`、`app-test:<app>`、`app-summary`、`app-config` 及所有结束标记；勿手工批量重排、转义或删改源码。
- `scripts/ci/materialize_test_hooks.py --app APP --kind meta` 在 Actions checkout 中恢复 `application/APP/meta-app/meta-app.sh`；`--kind test`（默认）恢复 `application/APP/test/test.sh`。工作流必须先生成文件，再枚举/读取/执行对应路径。生成器不能覆盖不同内容或符号链接，不会在宿主上执行 Shell。当前基线：24 个应用、30 个 Target、23 份 Meta-app、24 份 Test；`ffmpeg` 不存在有效的 Meta-app 脚本，不应无依据制造版本探针。
- 每个应用的 `application/APP/build/` 保留 Dockerfile 及其 `COPY`、`ADD`、构建步骤依赖。清理每应用文件之前要检查构建上下文、工作流与跨仓库引用；不要从文件名或重复 SHA 直接推定可以删除。具体目录及命令见本文件下方「应用目录与命令」章节。

### 应用目录与命令 / Application layout

新增应用以 `application/<app>/build/` 为最小构建目录，保留 Dockerfile 和所有 `COPY`、`ADD` 及构建阶段使用的静态文件。可以存在多个 Dockerfile；每个 Target 应在 README `app-config` JSON 中声明对应 Dockerfile、平台、基础镜像和标签策略。

元数据与镜像内测试的 **源码只维护在 README Applications 表格**。工作流运行时按需生成 `application/<app>/meta-app/meta-app.sh`（`--kind meta`）和 `application/<app>/test/test.sh`（默认 `--kind test`），而不是重新向仓库加入两份重复的持久化脚本。`ffmpeg` 的 Meta-app 缺失状态要保留，除非另有经验证的探针实施决策。

常用只读命令（仓库根目录运行）：

```bash
python3 scripts/ci/catalog.py validate
python3 scripts/ci/catalog.py matrix --kind build
python3 scripts/ci/catalog.py get --app runner --tag actions
python3 scripts/ci/catalog.py env --app runner --tag actions
python3 scripts/ci/catalog.py tags --app runner --tag actions --version 1.0 --consistent true
```

经明确授权的配置维护示例（只修改 `app-config` 以及其生成展示，不发布镜像）：

```bash
python3 scripts/ci/catalog.py set --app runner --field base_image --value debian:testing-slim
python3 scripts/ci/catalog.py set --scope target --app samba --tag alpine --field base_image --value alpine:latest
python3 scripts/ci/catalog.py set --scope target --app runner --tag actions --field dockerfile --value actions.Dockerfile
python3 scripts/ci/catalog.py set --scope app --app vlmcsd --field platforms --value linux/amd64,linux/arm64,linux/386
python3 scripts/ci/catalog.py summary --check
```

不要将旧 `app-version-table`、`app-version-json` 或旧版 `image_probe` 的配置方式视为当前生产结构；这些是下面历史文档记录的先前阶段。`novnc` 与 `novnc_alpine` 的同一发布标签冲突未自动修复；生产、Dev 和兼容工作流的发布路径需要各自验证。

### 工作流及发布边界

- 正式定时构建与发布入口为 `.github/workflows/docker_allinone.yml`；独立监控是 `monitor-images.yml`；`docker_allinone_gpt.yml` 承担非发布回归；`docker_allinone_dev.yml` 提供实验与 Dev 入口；`diagnostics.yml` 提供诊断。检查真实触发条件、权限和依赖，不要根据旧文档判断某 YAML 是否仍存在。
- 保留 `pull_artifact-dev.yml`、`download_artifact.yml` 的独立用途。对于其余共享/兼容工作流，先搜索 `uses: ./.github/workflows/...`、`workflow_call`、手动和外部 `repository_dispatch` 使用方，再考虑合并/删除；仓库内部未找到调用者不代表没有外部消费者。
- **`execution_route=dev` 且 `dev_mode=preflight`** 是已知的非发布预检路径；Dev `auto`/`build` 或 `promote-*` 有可能创建 Release 或向 Docker Hub/GHCR 发布。不要将这些模式当成 dry run。未获单独授权，禁止更改正式 Registry/Tag/Release、上传镜像、删除历史镜像或操作密钥。
- 检查、构建、应用测试、发布是不同的验证等级。只通过版本探针、配置校验或跳过了发布的 Actions Job，不能据此声称全链路发布等价。镜像平台、Base image、标签策略、Artifact 命名、监控语义及独立工具应保持兼容，变动要有对应实测证据。

### 修改后必检项

```bash
python3 scripts/ci/catalog.py validate
python3 scripts/ci/catalog.py summary --check
python3 scripts/ci/catalog.py matrix --kind version
python3 scripts/ci/catalog.py matrix --kind build
python3 -m unittest discover -s scripts/ci -p 'test_*.py' -v
python3 scripts/ci/test-workflow-graph.py
```

- 若确实修改了 `config`，使用 `catalog.py set` 或先修改 JSON 再运行 `catalog.py summary --write`；不应使用 `summary --write` 来补救 Meta-app/Test 源码丢失或错误引用。
- 比较 README 重写前后的 `config`、`monitor.records`、24 个应用行及全部 Meta-app/Test 脚本源码；验证无损 HTML 编解码、幂等、不覆盖非生成文件、`ffmpeg` 缺失语义、文件末尾表格位置。工作流变更时再检查 YAML 语法和内部调用关系；非发布 Actions 的成功不能替代生产发布验收。

## 历史研究与迁移记录 / Historical archive

以下内容逐份保留原 `docs/` 文档的叙述、历史 SHA、决策及测试证据。由于这些文档涵盖了不同阶段，部分“现有”“保持不变”“后续候选”等表述只适用于对应历史时间点；**不得据此直接实施删除、发布或调整触发条件**。历史信息与本文件前部“当前维护规范”冲突时，以当前仓库实际内容、实时测试和用户最新授权为准。

### 历史文件 A — Application file simplification

> 来源：`docs/application-simplification.md`（本次删除）；原 Blob：`b213d9f61525b201a5524185af942d1a775acbba`。以下为**历史记录**，非当前操作指令。

#### Application file simplification — phase 1

Baseline: `main@91103299b7ad2d65f9d2389ff56d3461386b2b71` contained 24 canonical applications and 91 tracked files below their directories (not counting `application/.example` or `application/route.md`): 23 upstream `meta-app.sh` and 24 built-image `test.sh`.

Phase 1 removes five committed `test/test.sh` files from `aria2`, `curl`, `privoxy`, `squid`, and `dnscrypt-proxy`; a shared POSIX probe (`scripts/ci/probe-image.sh`) now determines the actual installed version from inside each built image.

The legacy production, Dev, GPT and compatibility workflow code continues to search `application/<app>/test/*.sh`. It first runs `scripts/ci/materialize_test_hooks.py --app APP`, which creates **an untracked, ephemeral** `test.sh` with identical invocation behavior for the five supported apps; other applications retain their committed tests. `.gitignore` excludes only the five generated hook paths.

The shared probe output contract remains `version=<actual-installed-version>`; the upstream `meta-app` scripts are unchanged. Neither build context / Dockerfile nor Registry / Tag / Release logic is modified.

##### Evidence and scope

- First parity commit `ce61fe73` ran a real `linux/amd64` Buildx five-image comparison, and all five generated shared parser values matched the independently committed legacy `test.sh` values.
- Second commit `f6251b2` removed the five scripts and regenerated them at runtime; the subsequent real five-image AMD64 parity jobs passed.
- Third commit `3fa6449b` adds a 5×2 platform `linux/amd64` / `linux/arm64` nonpublishing parity matrix (requires final live Actions completion evidence).
- `scripts/ci/test_probe_image.py` tests POSIX parsing, invalid profiles, empty version and multiline rejection.
- `scripts/ci/test_materialize_test_hooks.py` tests five profile generation, idempotence, refusal to overwrite independent scripts, and identical wrapper output.
- All existing 24 apps, 30 build targets, base images, repositories and tag policies remain in README Schema v2.

##### Next migration candidates

1. Move additional simple `test.sh` rules to `probe-image.sh` after per-image live parity, keeping more complex SD.Next/ROCm and OpenWrt/runner tests unchanged until separate experiments.
2. Introduce a declarative upstream version strategy in README catalog before deleting `meta-app.sh`; never replace upstream probes by expected Docker labels.
3. Investigate `ttrss` metadata probe/test currently mirroring `vlmcsd` despite having a TTRSS Dockerfile, and its Dockerfile resource references, without unsafe deletion or rewriting.
4. Check FFmpeg's extra Dockerfile variants and SD.Next startup files for build-context dependencies before touching them.

Release/build parity is **not** proven by five isolated image-version checks. Production check → build → test → publish has not been executed by this migration.

Phase 2: README `config.apps.<app>.image_probe` became the canonical command and extractor for the original five; commit `9c0234f` passed 5×2 real architecture smoke and read-only unit tests. `doh-nosni` is a sixth declarative profile using `dnscrypt-proxy -version` with first-line extraction. Its previously tracked `test.sh` is removed in the next incremental commit, with a separate multi-stage Dockerfile smoke requirement. Other non-declarative applications retain their scripts.

Phase 4: all 24 complete test scripts are embedded in one expandable README HTML table, with deterministic HTML entity encoding for special characters. The legacy 18 `test.sh` files are copied byte-for-byte; six previously shared image probes use equivalent shell routines. The new materializer reads README by stable per-app markers, validates names and encoding, and recreates the original test path in the Actions workspace. Existing 18 scripts remain as independent test oracles until the smoke and byte-equivalence gates pass.

Phase 5 — duplicate-file retirement: after GitHub Actions validated 24/24 README embedded source snippets and compared all 18 still-existing shell sources byte-for-byte, the 18 tracked test/test.sh copies are removed. `docker_allinone_gpt.yml`'s two remaining hardcoded test paths (vlmcsd per-arch and local-registry matrix) now call the shared materializer explicitly before accessing the test file. The 24 apps' build inputs and all upstream meta-app probes remain unchanged. Fully representative production releases are outside this migration's test coverage.

README consolidation: the separate application-test table has been merged into the `Applications / 应用清单` main table, placing the complete test code behind per-row expandable Test controls. The `app-summary` markers now wrap both display fields and canonical test scripts; catalog/monitor regeneration preserves exact encoded tests and rejects missing or swapped script rows.

### 历史文件 B — CI pipeline phase 1

> 来源：`docs/ci-pipeline-phase1.md`（本次删除）；原 Blob：`666d562c3c913271c3fda3a835b1e80203c21055`。以下为**历史记录**，非当前操作指令。

#### CI Pipeline Phase 1 (Historical)

> Historical design note. Starting 2026-10-15, `version-compare-build.yml` was removed during workflow consolidation. The details below describe the former layout, not necessarily current workflow availability. See [Workflow Consolidation](#历史文件-d-workflow-consolidation) for current decisions.

This note documents the phase 1 split of monitor/build/publish responsibilities.

##### What Changed

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

##### Stable README Rules

The generated README section no longer contains volatile run metadata:

- No refresh timestamp.
- No per-app `updated_at`.
- No run id, duration, or runner host.

The README version JSON keeps stable keys sorted by `json.dumps(sort_keys=True)`.

##### Compatibility

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

##### Recommended Usage

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

##### Follow-Up Decisions

- Decide whether `version-compare-build.yml` should eventually be removed.
- Decide whether `build-docker_indocker.yml` remains supported.
- Decide whether README should be updated only after successful publish rather than after monitor.
- Decide whether publish failures should remain `continue-on-error` or become blocking.

### 历史文件 C — Markdown-only catalog lab

> 来源：`docs/markdown-table-lab.md`（本次删除）；原 Blob：`f089df593a661f7051053011cfa38a1d311ff5e3`。以下为**历史记录**，非当前操作指令。

#### Markdown-only catalog feasibility lab

**Non-production / 仅研究** — no `docker_allinone.yml`, `monitor_state.py`, or `catalog.py` write path reads this prototype.

Run `python3 -m unittest discover -s scripts/ci -p 'test_table_catalog_lab.py' -v`.

The lab renders a strict **18-column, 30-row Markdown table** from the current schema-v2
README JSON, then parses it back and compares all 24 application definitions, 30
build targets, and 24 historical monitor observations for lossless equivalence.

One row per target means monitoring observations are duplicated for multi-target
applications (runner, samba, adguardvpn-cli). The parser rejects inconsistent
repeated monitor data, duplicate targets, missing columns and invalid escapes.

**Trade-off:** Complete removal of JSON is possible, but a 18-column table is harder
to maintain than the 8-column visible table and combined structured JSON. This
prototype is intentionally isolated; a cutover requires safe atomic writes, escaping
rules, conflict handling, backward compatibility, and full check/build/publish tests.

Schema-v2 `image_probe` is preserved losslessly in the `Image probe JSON` column; this is a research-only codec, not a new production data source.

### 历史文件 D — Workflow consolidation

> 来源：`docs/workflow-consolidation.md`（本次删除）；原 Blob：`27a623fec6ae5bf7bc59a20fa426742a4c22997a`。以下为**历史记录**，非当前操作指令。

#### Docker workflow consolidation — stage 1 (2026-10-15)

##### Scope and intent

Use recently exercised GitHub Actions workflows as migration anchors, preserving independent artifact utilities. This stage removes three superseded entry points and stops repeated automatic execution of transitional build workflows. Production build, tag, publish, archive, application and platform logic is intentionally unchanged.

##### Protected migration anchors (seven)

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

##### Retired workflows

| File | Reason and replacement |
| --- | --- |
| `call-build.yml` | Obsolete manually dispatched matrix calling `build-docker.yml`. The production `docker_allinone.yml` contains all 24 explicit app/tag combinations, including the dynamically discovered `curl:latest`; `call-build_dev.yml` remains as a compatibility/testing reference. |
| `matrix.yml` | Separate base-image layer matrix plus build/push pipeline. Its daily/automatic role is superseded by the production All in One prepare/check/build path; it has no internal workflow callers. |
| `version-compare-build.yml` | Duplicate version monitor, README renderer and conditional build coordinator. The production All in One already invokes `scripts/ci/monitor_state.py` and conditionally builds changed targets. |

Removed workflows were not directly referenced by other workflow files at this baseline. External `repository_dispatch` clients are **not** provably absent; any such integrations must migrate to an active entry point.

##### Remaining legacy workflows (not deleted)

`baseimage_dev.yml`, `build-docker.yml`, `build-docker_indocker.yml`, `call-fetch_dev.yml`, `call-fetch_stable.yml`, `callable-fetch-app-version.yml`, `callable-fetch-layers.yml`, `image-pipeline.yml` and `meta-app_dev.yml`.

In particular, `monitor-images.yml` still calls `callable-fetch-app-version.yml`, `call-build_dev.yml` still calls `build-docker_indocker.yml`, `image-pipeline.yml` still calls `build-docker.yml`, and `call-fetch_dev.yml` still calls `callable-fetch-layers.yml`. Do not remove those callees before callers are migrated.

##### Required behavior and verification

- No change to `application/*`, `vars.env`, Dockerfiles, build/test scripts, base images, platform lists, Docker Hub/GHCR tags or GitHub Release asset format.
- No direct secret changes, image publication or explicit Actions dispatch in this stage.
- Source checks: all seven protected workflow files remain present; both transitional workflows retain `workflow_dispatch` and `repository_dispatch`, but have no `schedule`; production and monitor schedules remain.
- Validate future production and monitor scheduled jobs separately. A successful monitoring run or a production run that skips build jobs does **not** prove the publish path.
- Future integration: migrate the useful dry-run/matrix selection from `image-pipeline.yml`, comparison and promotion decisions from Dev, and isolated smoke/artifact evidence from GPT. Verify production equivalence before retiring their old sources.
- Production failure gates (check status, test outcome, registry push) and cross-registry parity still require follow-up; they were **not** modified by this commit.

Rollback: revert the consolidation commit on `main` to restore the removed YAML entry points and former automatic triggers. Avoid force-pushing branch history.

##### Stage 2 — main workflow inventory and retirement gates (2026-10-16)

Baseline: `main@c882d6921ae830bed3cebbb9f6a5aab437210548`. This stage is a read-only YAML audit recorded here, not authorization to delete protected workflows or alter production publication.

- **16** workflow YAML files, **8632** source lines (approximately **334.3 KiB**).
- The three largest: `docker_allinone_gpt.yml` (2,042 lines), `docker_allinone_dev.yml` (1,446), and `docker_allinone.yml` (1,331). They account for **55.8%** of all workflow lines; reducing count alone will not remove most duplicated logic.
- README JSON schema v2 remains the single source for 24 applications and 30 targets. Neither Markdown-only lab nor generated application summary is a production configuration source.

###### Verified internal reusable-workflow edges

```text
docker_allinone.yml --------+
                            +--> callable-fetch-app-version.yml
monitor-images.yml ---------+

call-build_dev.yml ------------> build-docker_indocker.yml
image-pipeline.yml ------------> build-docker.yml (dry-run and publish branches)
call-fetch_dev.yml ------------> callable-fetch-layers.yml
```

Do not remove a callee while one of these caller edges remains. External `repository_dispatch`, manual automation, and downstream reusable-workflow consumers are not established by an internal source audit.

###### Workflows to preserve during incremental migration

| Class | Workflows | Reason |
|---|---|---|
| Production | `docker_allinone.yml` | Only intended authoritative build/publish entry; keep its existing triggers and tags |
| Independent monitor | `monitor-images.yml` | Separate successful monitoring path; its daily schedule overlaps production at 01:00 UTC but must not be retired before tested parity |
| Test and research | `docker_allinone_gpt.yml`, `docker_allinone_dev.yml` | Retain guarded smoke/comparison and promotion research, particularly non-publishing checks |
| Compatibility matrix | `call-build_dev.yml` | Current caller of containerized builder; explicitly protected migration anchor |
| Standalone utilities | `pull_artifact-dev.yml`, `download_artifact.yml` | Independent user workflows; not building-block deletion candidates |

###### Nine other workflows and first-pass disposition

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

###### Implementation order and acceptance criteria

1. **No-publication parity:** compare outputs of layer inspectors and metadata probes on fixed immutable image digests; record platform, output JSON, Artifact names, and exit status. Do not delete originals first.
2. **Thin diagnostic entry points:** consolidate `baseimage_dev.yml`, `call-fetch_stable.yml`, and `meta-app_dev.yml` only when equivalent on-demand functionality has a verified replacement. Retain `call-fetch_dev.yml` and `callable-fetch-layers.yml` until that comparison is complete.
3. **Experimental build migration:** bring the useful `image-pipeline.yml` dry-run/matrix behavior into `docker_allinone_dev.yml`; ensure publishing remains off by default. Only then consider removing `image-pipeline.yml` and `build-docker.yml`.
4. **Containerized compatibility:** preserve `call-build_dev.yml` until `build-docker_indocker.yml` behavior has been validated or intentionally superseded; do not silently abandon `workflow_call` clients.
5. **Production and monitoring:** after full check → build → test → publish validation, evaluate sharing version probe code and daily monitoring runs. Keep the two existing schedules until explicit validation and approval to merge.
6. **Cleanup gate:** run GitHub Actions YAML validation, scan every internal `uses: ./.github/workflows/...` reference, compare current 24-app/30-target matrix, and inspect non-publishing Actions results before an individual workflow is retired. No forced pushes or registry tag changes.

Stage-2 inventory itself changes **documentation only**; zero workflows removed or modified at this audit checkpoint.



###### Stage 2 integration checkpoint — shared production dispatcher

`docker_allinone.yml` now presents `execution_route: production|dev` on manual dispatch. `production` is the unchanged default for cron/repository dispatch, and the existing `prepare` job is skipped on Dev-only manual invocations. `dev` calls `.github/workflows/docker_allinone_dev.yml` through `workflow_call`, preserving `auto`, `build`, and dedicated promotion modes, including optional `target_id` and promotion version/revision inputs. The Dev YAML remains independently manually dispatchable until this wrapper path is actually tested. No production image publishing was initiated by this change; GitHub Actions syntax validation and static routing tests do not prove a live Dev promotion.


##### Stage 2 completed non-production layer consolidation (2026-10-16)

The new `diagnostics.yml` is the single manual diagnostics entry for app-version probes and OCI layer inspection. Internally it reuses `callable-fetch-app-version.yml` and `callable-fetch-layers.yml`. The `platform-details` matrix preserves the historical `layers-<image>-<arch>/layers.json` and `layer-info-<image>-<arch>/image_*.json` artifact schemas. A new `collect` job uploads `diagnostics-layer-summary` containing `base_layers.json` and `aggregated_layers.json`.

Verified on `main` before retirement:
- `38868334453`: version + per-image layer artifacts, including explicit contract check — success.
- `38868702585`, `38868775865`: per-arch raw inspect and layers compatibility artifacts — success.
- `38869143288`: all five selected images × amd64/arm64 detailed probes; 26 Artifacts, full compatibility validation — success.
- `38869288771`: layer aggregation and final artifact contract — success.
- `38869062943`: Production All-in-One -> reusable Dev preflight, no monitor/build/publish in Dev route — success.

With those tests successful, retire `baseimage_dev.yml`, `call-fetch_stable.yml`, and `call-fetch_dev.yml`. `callable-fetch-layers.yml` stays as an internal callee. Legacy `repository_dispatch` consumers of the deleted files were not discoverable in the repository; external clients must use `diagnostics.yml` manual dispatch. The old `baseimage_dev.yml` path-scoped pull-request trigger was not carried over automatically. `meta-app_dev.yml` remains until its all-platform probing behavior is reviewed; the canonical version probe currently uses a preferred platform. Legacy Docker/GHCR promotion remains separately implemented in Dev and must not be deleted until real publishing parity is tested.

###### Post-retirement live verification / 实际验收

- Three superseded YAML entries removed on `main@ded3cba2`: `baseimage_dev.yml`, `call-fetch_stable.yml`, `call-fetch_dev.yml`. This reduces the workflow **entry count 16 -> 14** after adding `diagnostics.yml`.
- Version: `diagnostics.yml` delegates to `callable-fetch-app-version.yml` (non-publishing `vlmcsd` run verified).
- Layers: `diagnostics.yml` delegates to `callable-fetch-layers.yml`, and runs a per-architecture Skopeo compatibility matrix producing the former artifact structures; the new aggregator emits `diagnostics-layer-summary`.
- Real runs: `38869143288` validated 5 images × 2 architectures; `38869288771` validated aggregation; `38869484554` passed 24 configuration tests, 5 table-lab tests, 2 aggregator tests and a 14-workflow dependency guard.
- Production/Dev routing: `38869062943` invoked `docker_allinone.yml` as a reusable workflow in Dev preflight mode. Dev ran only read-only checks and all production publishing jobs were skipped.
- **Not yet proven:** real Dev build/GHCR promotion, end-to-end production publication, legacy meta-app all-platform equivalent behavior. `docker_allinone_dev.yml` and `meta-app_dev.yml` must remain until these are validated.

Removed workflow names must not be silently referenced by external automation. The replacement `diagnostics.yml` exposes a manual profile (`stable` five images / `base` three images), optional single-image override, and version probe inputs.

**Safe Dev default correction.** `execution_route=dev` now defaults to `dev_mode=preflight`; users must explicitly select `auto`, `build`, or a `promote-*` mode. Code review confirms Dev `auto`/`build` can create GitHub Releases and push Docker Hub/GHCR tags when a candidate needs promotion. Neither is a dry-run mode. Do not use these modes for nonpublishing integration tests. The existing GPT nested `preflight` test remains the only verified production-to-Dev execution route.

### 历史文件 E — Application layout / route.md

> 来源：`application/route.md`（本次删除）；原 Blob：`aaa0a664aee9fc4f98ad811b76f6eb0e7e7430c9`。以下为**历史记录**，保留旧阶段配置及文件布局描述供追溯，不能覆盖前部现行规范。

#### docker-builder application layout

The canonical app and target configuration is the JSON block in
[README.md](README.md) between the app-config markers. It replaces
per-app env/vars.env, build/build.sh and push/tag_version.sh.

Use this directory structure for a new app:

    application/<app>/
    ├── build/
    │   ├── Dockerfile
    │   └── any files used by COPY, ADD or Dockerfile build steps
    ├── meta-app/
    │   └── meta-app.sh
    └── test/
        └── test.sh

Multiple Dockerfiles, build support scripts and configuration assets remain
inside build/; each target names its Dockerfile in the root README catalog.

To manage configs from the repository root:

    python3 scripts/ci/catalog.py validate
    python3 scripts/ci/catalog.py matrix --kind build
    python3 scripts/ci/catalog.py get --app runner --tag actions
    python3 scripts/ci/catalog.py env --app runner --tag actions
    python3 scripts/ci/catalog.py tags --app runner --tag actions --version 1.0 --consistent true

Supported simple write (only affects app-config):

    python3 scripts/ci/catalog.py set --app runner --field base_image --value debian:testing-slim

For target additions or changes to platforms, edit the single JSON block,
run validate and the non-publishing GPT Actions smoke before relying on
the production workflow. The app-version-table and app-version-json sections
are generated runtime state, not configuration inputs.

Existing compatibility notes:
- Both novnc and novnc_alpine currently target grinch27/novnc:latest.
  The parser reports this pre-existing ownership conflict; it does not
  change published tags without an explicit decision.
- samba:alpine now uses alpine.Dockerfile with alpine:latest base image.
- Legacy manual/Dev workflows consume the shared catalog and generic
  build executor; their full publishing paths need separate regression.

Target-specific update example (preserves all other README sections):

    python3 scripts/ci/catalog.py set --scope target --app samba --tag alpine --field base_image --value alpine:latest
    python3 scripts/ci/catalog.py set --scope target --app runner --tag actions --field dockerfile --value actions.Dockerfile

Application platform update:

    python3 scripts/ci/catalog.py set --scope app --app vlmcsd --field platforms --value linux/amd64,linux/arm64,linux/386

README's human-readable `app-summary` is derived from the canonical `app-config` JSON. The `catalog.py set` operation updates both atomically; after manually editing the JSON run `python3 scripts/ci/catalog.py summary --write` followed by `summary --check`. Collapsible JSON containers are presentation only and do not affect Actions.

Unified README data schema v2: a single `app-config` fenced JSON document contains `config` (reviewed static settings) and `monitor.records` (Actions-owned historical observations). The visible table combines both. The legacy separate version JSON is removed; the parser retains read-only compatibility for historical v1 documents. Do not edit `monitor.records` manually unless restoring an audited snapshot.

Shared actual-image probe migration: `scripts/ci/probe-image.sh` supports `aria2`, `curl`, `privoxy`, `squid`, and `dnscrypt-proxy` via `sh probe-image.sh APP` executed inside the built image. Do not remove application test scripts until the non-publishing `[probe-smoke]` parity matrix and every caller migration pass. Expected upstream version and actual installed version remain separate.

P1 runtime migration: five simple image version hooks are now **generated only in the Actions workspace** by `python3 scripts/ci/materialize_test_hooks.py --app APP`. The generator embeds the shared POSIX `probe-image.sh` logic into the legacy `application/APP/test/test.sh` execution path, allowing existing production, Dev, GPT and compatibility build jobs to run unchanged tests while no longer committing five redundant per-app scripts. Calls must occur before scanning `test/*.sh` or checking whether the `test/` directory exists. Do not use generated files as permanent repository sources.

Declarative image tests (Phase 2): `README.md` Schema v2 `config.apps.<app>.image_probe` contains an `argv` array and an `extract` descriptor (`first_line`, `first_field` or `prefix_field`). `scripts/ci/materialize_test_hooks.py` validates these fields and creates a short `test.sh` in the Actions checkout only. It does not evaluate arbitrary shell snippets from README. The old `scripts/ci/probe-image.sh` is a temporary test oracle for the first five profiles and not the production configuration source.

The same declarative `first_line` extractor now covers `doh-nosni` (installed `dnscrypt-proxy -version`). Its custom multi-stage Dockerfile is unchanged; both architectures remain gated by non-publishing Buildx parity.

All 24 built-image tests are now stored **in an expandable HTML table in root README.md** (24 rows, one per application), enclosed by `app-tests` and per-app `app-test` markers. Scripts retain exact POSIX shell source; HTML escape codes preserve newline and pipe within table cells. `scripts/ci/materialize_test_hooks.py` generates the legacy `application/<app>/test/test.sh` only in the Actions checkout. The 18 original files are retained during byte-for-byte parity validation and are to be retired only after test success. The six previously declarative `image_probe` values are now replaced by scripts in that table; the production JSON still solely controls build settings and monitored state.

The `Applications / 应用清单` Markdown table includes a ninth **Test** column, with one expandable `<details><pre><code>` shell script per application. The former standalone `Application test scripts` section has been removed. Test markers stay inside `app-summary`; catalog and monitor regeneration parse the existing scripts first, preserving all 24 script bodies. Scripts only execute inside the built container.


###### README-embedded meta-app scripts

The Applications table now contains 23 expandable upstream metadata scripts;
ffmpeg deliberately has no metadata probe. Run `python3 scripts/ci/materialize_test_hooks.py --app APP --kind meta` before scanning `application/APP/meta-app/*.sh`.
The generator preserves original shell source and does not execute it on the host.
`--kind test` remains the default for built-image testing.
