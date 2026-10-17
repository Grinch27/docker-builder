# AGENTS.md — docker-builder

适用于仓库根目录及所有子目录。先核对当前源码、GitHub Run 和用户最新要求，再修改；历史描述与当前源码冲突时以实测为准。

## 当前状态

截至 2026-10-17，已验收的代码提交为 [`95bb3fa`](https://github.com/Grinch27/docker-builder/commit/95bb3fac6a42409192c15f942d5212c5369943f1)。当前有 **15 个工作流文件：原 14 个 + `gpt_dev.yml` 合并候选**。核心能力已并入候选的 18 个普通 Jobs，无嵌套工作流调用；正式入口尚未替换，因此文件数量精简尚未落地。目标是一个核心工作流，另保留两个独立 Artifact 工具。

| 入口 | 当前职责 |
|---|---|
| `.github/workflows/gpt_dev.yml` | 合并候选，push / 手动非发布验收，默认 `verification` |
| `.github/workflows/docker_allinone.yml` | 正式定时检查、构建、发布；手动 Dev 路由 |
| `.github/workflows/docker_allinone_dev.yml` | Dev 预检、构建、晋升；部分模式会发布 |
| `.github/workflows/docker_allinone_gpt.yml` | 原非发布回归入口 |
| `.github/workflows/monitor-images.yml` | 独立版本监控 |
| `.github/workflows/diagnostics.yml` | 版本、OCI 层及平台诊断 |
| `.github/workflows/pull_artifact-dev.yml`、`download_artifact.yml` | 保留独立的镜像导出、Artifact 下载与处理用途 |

其余 7 个共享或兼容入口仍在使用：`build-docker.yml`、`build-docker_indocker.yml`、`call-build_dev.yml`、`callable-fetch-app-version.yml`、`callable-fetch-layers.yml`、`image-pipeline.yml`、`meta-app_dev.yml`。删除前必须检查内部调用与外部消费者；仓库内没有调用者不能证明没有外部 `workflow_call` / `repository_dispatch` 使用方。

### 已完成的实际验收

- 第一轮：[`39026138786`](https://github.com/Grinch27/docker-builder/actions/runs/39026138786)，提交 `d913873`，成功。读取成功日志仍发现强制构建标志丢失、不同架构导出包含相同平台集合两个问题，随后修正。
- 修正轮：[`39026725070`](https://github.com/Grinch27/docker-builder/actions/runs/39026725070)，提交 `95bb3fa`，**23 个 Jobs 成功、5 个跳过**。18 个 Jobs 经矩阵展开共 28 个实例。
- 90 项单元测试；8 个应用/平台构建与镜像内测试组合；3 个本地 Registry 往返测试均通过。`vlmcsd` 的 amd64 / arm64 / 386 检查、强制构建、镜像测试、导出及 xz 压缩通过；版本、层诊断和 Artifact 校验通过。
- 日志确认 `plan=true check=true`、`forced=true changed=true publish=false`。逐平台导出验证为 `linux/amd64`、`linux/arm64`、`linux/386`，三个归档 SHA256 不同。
- Registry 登录、外部镜像推送、GitHub Release 发布均跳过。候选写入步骤禁用，原正式工作流和应用构建源码在上述迁移提交中未改动。

以上证明代表性非发布路径通过，**不证明全部 52 个 Target/平台组合、正式发布、Dev 晋升或容器构建路径通过**。`verification` 的 8 个组合为 aria2:latest × amd64/arm64、samba:alpine × amd64/arm64、vlmcsd:latest × amd64/arm64/386、runner:actions-slim × amd64；本地 Registry 测试为 aria2、samba、vlmcsd 的 amd64。

## 配置、脚本与目录

`README.md` 文末 Applications 表格是唯一维护源，固定保留 **Application / JSON / Build / Meta-app / Test** 五列：

- JSON：每个 `app-json:<app>` 单元格保存 `app`、`config`、`monitor`。人工维护 `config`；自动化只更新 `monitor`。解析后对应文档的 `monitor.records`，不是独立 `app-config` 块。
- Meta-app / Test：完整 Shell 源码，分别用于上游版本探针、镜像内测试。保留 HTML 实体编码及全部起止标记，不能用摘要、占位符或预期版本标签代替实际测试。
- Build：由 JSON 为全部 30 个 Target 生成 `--output type=cacheonly` 示例；保留此列，使用生成器更新，不手工维护重复脚本。

当前基线：**24 个应用、30 个 Target、52 个 Target/平台组合、23 份 Meta-app、24 份 Test**。`ffmpeg` 没有有效的 Meta-app 探针，保留缺失语义。`app-summary`、`app-json`、`app-build`、`app-meta`、`app-test` 标记及表格位于文件末尾的约定必须保留。精简 README 说明时，不删除其中可执行配置和源码。

新增应用保留 `application/<app>/build/` 中的 Dockerfile、`COPY` / `ADD` 文件及构建阶段依赖；每个 Target 在对应 JSON.config 中声明 Dockerfile、平台、基础镜像和标签策略。清理文件前检查构建上下文及跨仓库引用，不能只凭文件名或相同 SHA 判断可删除。

运行时恢复脚本，再扫描或执行对应目录：

```bash
python3 scripts/ci/materialize_test_hooks.py --app APP --kind meta
python3 scripts/ci/materialize_test_hooks.py --app APP --kind test
```

生成路径为 `application/APP/meta-app/meta-app.sh`、`application/APP/test/test.sh`，仅用于 Actions 工作区，不重新提交重复副本。生成器不执行 Shell，拒绝覆盖不同内容或符号链接。

## 共享实现与变更约束

| 文件 | 职责与约束 |
|---|---|
| `scripts/ci/catalog.py` | 读取表格 JSON、生成矩阵和展示列、维护配置与标签策略 |
| `scripts/ci/materialize_test_hooks.py` | 从表格恢复 Meta-app / Test 的完整源码 |
| `scripts/ci/build-image.sh` | 共用 Buildx 命令，生产默认 `registry`，Dev/GPT 使用 `load` |
| `scripts/ci/workflow_plan.py` | 路由和矩阵选择；候选必须经过 `staging_plan` 的非发布限制 |
| `scripts/ci/monitor_state.py` | 监控状态、变更矩阵及稳定 README 展示 |
| `scripts/ci/gpt_workflow_graph.py` | 候选普通 Jobs 的依赖、循环、嵌套调用检查 |
| `scripts/ci/test-workflow-graph.py` | 原 14 个工作流依赖保护；仅排除候选，不可据此宣称仅有 14 个文件 |
| `scripts/ci/verify_image_archive.py` | 不解压、不执行归档；验证唯一 manifest、平台配置和层文件 |

强制构建用显式布尔比较合并 matrix 与 plan 值，避免字符串 `"false"` 被 `||` 视为真值而覆盖强制请求。运行时门禁必须确认强制标志没有丢失。

逐平台归档使用 `docker image save --platform "$platform"`，随后运行归档验证器。默认 save 会包含本地所有平台变体，不能用于冒充逐架构导出。该选项需要 Docker API 1.48+，见 [Docker 官方说明](https://docs.docker.com/reference/cli/docker/image/save/)。

保持平台、基础镜像、Registry、Tag、版本 Label、Artifact 名称与格式、监控语义兼容。新增或改动脚本时，在文件头记录需求、未知项、风险和验证方式。修复依据实际日志；不得用跳过失败、弱化测试或篡改版本值换取绿色状态。

## 验证命令

在仓库根目录运行：

```bash
python3 scripts/ci/catalog.py validate
python3 scripts/ci/catalog.py summary --check
python3 scripts/ci/catalog.py matrix --kind version
python3 scripts/ci/catalog.py matrix --kind build
python3 -m unittest discover -s scripts/ci -p 'test_*.py' -v
python3 scripts/ci/test-workflow-graph.py
python3 scripts/ci/gpt_workflow_graph.py
```

配置变更优先使用 `catalog.py set`；手改对应 JSON.config 后运行 `python3 scripts/ci/catalog.py summary --write`，然后重新检查。示例：

```bash
python3 scripts/ci/catalog.py set --scope target --app samba --tag alpine --field base_image --value alpine:latest
python3 scripts/ci/catalog.py set --scope app --app vlmcsd --field platforms --value linux/amd64,linux/arm64,linux/386
```

README 改写需比较全部 JSON 配置、监控记录、应用行和 Meta-app / Test 源码，检查生成幂等及末尾标记；不得用 `summary --write` 掩盖源码丢失。工作流变更再运行 YAML / Actions 表达式检查、调用关系检查，并读取实际 Actions 日志和产物。

验收环境使用 actionlint v1.7.12。它不识别 `concurrency.queue`，且对候选隔离用的 `if: false` 报常量提示；仅可精确忽略这两类已知提示。缺少 shellcheck / pyflakes 时应明确说明相应检查未执行，不把它们计为通过。不能为消除提示启用禁用的发布步骤。

## 发布边界与下一步

用户已授权候选推送、非发布测试、读取日志和迭代修正；本次文档整理不扩大为正式发布、密钥操作或旧入口退役。

候选 `WORKFLOW_READ_ONLY=true` 拒绝生产、容器发布和 Dev 晋升路由；发布步骤、README 推送、Dev/Container 发布 Jobs 另有硬禁用。这里描述的是执行门禁，候选 YAML 的 token 权限仍为 `write-all`。验证权限收窄的可行性属于后续工作。

正式 Dev 仅 `execution_route=dev` + `dev_mode=preflight` 是已验收的非发布预检；`auto` / `build` / `promote-*` 可能创建 Release 或推送 Docker Hub/GHCR，不能当作 dry run。检查、构建、镜像内测试、发布是不同验收等级；报告必须给出 Commit、Run、实际范围、跳过项及限制。

待办顺序：补齐合并候选的全量 52 组合与未选路由验证；单独完成发布及 Dev/Container 等价验收；核对外部调用方、触发器、权限和回滚方案；再切换正式入口、移除已迁移旧文件，并同步两个图检查器。当前生产与独立监控的重复定时触发仍存在。

已知事项：`novnc` 与 `novnc_alpine` 共享 `grinch27/novnc:latest`，不可静默改标签。历史应用构建失败需重新读取对应 SHA 的最新日志，不沿用旧成功/失败数字。保留 `application/.example/build/` 两份模板及 `application/ffmpeg/build/docker-ffmpeg.dockerfile` 上游参考。

## 历史资料

先前五份研究/迁移文档、历史 Run、已删除文件及其恢复链接统一保存在 [精简前 AGENTS 固定快照](https://github.com/Grinch27/docker-builder/blob/95bb3fac6a42409192c15f942d5212c5369943f1/AGENTS.md)。通过该提交读取或恢复原文；不再在现行规范中重复过时阶段描述。历史记录仅用于追溯，不构成当前发布或删除授权。回退用普通 revert，不强推分支历史。
