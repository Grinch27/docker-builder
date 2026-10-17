# AGENTS.md — docker-builder

适用于仓库根目录及所有子目录。先核对当前源码、GitHub Run 和用户最新要求，再修改；历史描述与当前源码冲突时以实测为准。

## 当前状态

截至 2026-10-17，初始代表性验收提交为 [`95bb3fa`](https://github.com/Grinch27/docker-builder/commit/95bb3fac6a42409192c15f942d5212c5369943f1)，后续全量与定向结果见下表。当前有 **15 个工作流文件：原 14 个 + `gpt_dev.yml` 合并候选**。核心能力已并入候选的 17 个普通 Jobs（校验已并入规划），无嵌套工作流调用；正式入口尚未替换，因此文件数量精简尚未落地。目标是一个核心工作流，另保留两个独立 Artifact 工具。

| 入口 | 当前职责 |
|---|---|
| `.github/workflows/gpt_dev.yml` | 合并候选，普通 push 默认 `validate`，手动默认 `verification`；`acceptance` 为完整矩阵及 Dev/Container 非发布验收 |
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

以上为初始代表性非发布验收，**不证明全部 52 个 Target/平台组合、正式发布或 Dev 晋升通过**。`verification` 的 8 个组合为 aria2:latest × amd64/arm64、samba:alpine × amd64/arm64、vlmcsd:latest × amd64/arm64/386、runner:actions-slim × amd64；本地 Registry 测试为 aria2、samba、vlmcsd 的 amd64。

### 全量与 Dev/Container 验收（2026-10-17）

| 范围 | 代码与运行 | 实际结果 |
|---|---|---|
| 完整配置矩阵 | `faefe3f` / [39028192731](https://github.com/Grinch27/docker-builder/actions/runs/39028192731) | 41/52 通过、11/52 失败；52 个唯一组合与 README 配置逐项一致，SD.Next Dev 通过 |
| Dev 构建、比较、归档 | 同上，Job `117383380616` | vlmcsd 的 amd64 / arm64 / 386 全通过，逐平台 tar 验证通过；晋升跳过 |
| Container 全链路 | `342a289` / [39028584662](https://github.com/Grinch27/docker-builder/actions/runs/39028584662) | vlmcsd 三架构元数据、强制构建、本地 Registry、Test、导出、xz、分卷、校验及说明生成通过；外部发布全部跳过 |
| 百度网盘定向重测 | `5a7ef20` / [39028873811](https://github.com/Grinch27/docker-builder/actions/runs/39028873811) | amd64 / arm64 构建及现有 README Test 均通过 |

本轮修正：Container 元数据恢复脚本改用实际克隆目录 `PATH_self`；平台检查分别核对 OS、架构、可选 Variant；验收 Artifact 名含 run attempt，避免重跑冲突。百度网盘改用同版本、同架构的百度官方直连 CDN，并从 GitHub 发布页跳转解析 noVNC/websockify 归档，避免匿名 API 未返回下载字段。未改平台、镜像标签及正式工作流。

### 阶段验收标准与应用待办

用户于 2026-10-17 调整标准：**约八成应用能成功构建即可，不再为个别应用持续追加修复；失败应用记录后留待以后处理。** 本阶段按此标准收尾，保留真实失败状态和现有测试门禁，不要求 52/52 全绿，也不通过删除矩阵项、忽略退出码或弱化 Test 提高成功率。

截至本次记录，完整运行 `faefe3f` 加百度网盘定向重测 `5a7ef20` 的已完成证据如下。应用通过要求该应用全部配置目标及平台均通过；Target 通过要求其全部配置平台均通过。

| 统计口径 | 首轮完整运行 | 加入百度网盘重测后的累计证据 |
|---|---|---|
| 应用 | 18/24（75.0%） | 19/24（79.2%，约八成） |
| Target | 24/30（80.0%） | 25/30（83.3%） |
| Target/平台组合 | 41/52（78.8%） | 43/52（82.7%） |

累计列跨不同 SHA，**不代表同一提交的全量通过，也不代表应用成功率严格超过 80%**。下面 5 个应用、9 个组合保留为后续待办，不阻塞本阶段工作流整合验收。百度网盘两架构已重测通过，不再列入失败待办。

| 待处理应用（均为 latest） | 首轮失败平台 | 已知原因与后续处理 |
|---|---|---|
| expressvpn | amd64、arm64、386、arm/v7 | 旧下载页未提供所需 `.deb` 链接，下载地址为空。后续核对官方包来源、CLI 迁移与 32 位兼容方案；本轮暂缓。 |
| ffmpeg | amd64 | Meson native file 使用双引号。`62dbd5a` 已改为单引号，本地 Meson 解析验证通过；[39033385954](https://github.com/Grinch27/docker-builder/actions/runs/39033385954) 重测仍在运行，尚未计为通过。 |
| sdnext | amd64 | Runner 根盘耗尽，Worker 日志也无法写入，根因已从 Check Run annotation 确认。`62dbd5a` 已给大型镜像 Job 增加仅限一次性 GitHub-hosted Runner 的空间清理；[39033385954](https://github.com/Grinch27/docker-builder/actions/runs/39033385954) 重测仍在运行，效果待确认。 |
| stable-diffusion-webui-amdgpu | amd64 | Python 3.12 构建 scikit-image 0.21.0 时 Pythran/C++ 标准不兼容。`3893ab4` 已对该源码构建设置 C++17 并增加实际导入检查；[39033539487](https://github.com/Grinch27/docker-builder/actions/runs/39033539487) 重测仍在运行，尚未计为通过。 |
| ttrss | amd64、arm64 | 缺少 Dockerfile 的 COPY 输入：`docker-entrypoint.sh`、`src/wait-for.sh`、`src/ttrss.nginx.conf`、`src/initialize.php`、`src/s6`。后续恢复并审查匹配版本的构建资源；本轮暂缓。 |

已启动的三项重测保留运行；截至 2026-10-17 21:03（Asia/Shanghai）仍在运行。本轮不再因这些应用追加修复或新一轮构建。后续处理时先读取对应 Run 的最终结论及日志，再更新本表，不把已提交修复等同于构建成功。状态是本次记录时的快照，不是自动更新的实时结果。

当前本地与 CI 为 106 项测试通过，含实际平台门禁、Meson 文件生成、目标筛选、规划失败门禁和镜像比较边界；最新轻量验收见下节。actionlint 仅精确忽略前述 queue / false 两类提示，shellcheck / pyflakes 未执行。Dev/Container 实测仅证明代表性 vlmcsd 目标，未验证所有应用、真实 Registry/Release 晋升、VPN 联网、GUI 或 GPU 运行。跨 SHA 的定向通过不得汇总成同一 SHA 的 52/52。

### 工作流精简验收（2026-10-17）

- `b5f71d3` / [39034643008](https://github.com/Grinch27/docker-builder/actions/runs/39034643008)：校验与规划合并，18 → 17 个 Jobs；普通 push 默认只运行 Runner 解析和校验/规划，实测 **2 成功、15 跳过**，99 项测试通过，`route=validate`、发布标志均为 `false`。
- `8474dac` / [39034967939](https://github.com/Grinch27/docker-builder/actions/runs/39034967939)：Dev/smoke 两份完全相同的 197 行比较代码提取为 `compare_image_snapshot.py`；实测 **2 成功、15 跳过、106 项测试通过**。原算法 AST 保持一致，本地 9 组固定输入的完整 JSON 输出与提取前逐字节相同。
- 候选 YAML 本轮由 **4,442 → 4,006 行**、178,539 → 161,053 字节。提取共享逻辑用于减少重复维护，不把转移到辅助脚本的代码计为业务逻辑删除；未据此声称运行时间提升百分比。
- 两段完全相同的 Docker 数据目录/压缩前清理脚本使用 [YAML Anchor/Alias](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations#yaml-anchors-and-aliases) 复用。解析后确认所有原始执行步骤保留，校验先于规划运行；失效校验不能被忽略。
- 候选 Dev/smoke 并发组改用 `gpt-dev-<ref>-<app>`、`gpt-smoke-<ref>-<target>`，与原入口隔离。push 路径覆盖 README 配置及全部 `scripts/ci/**`，普通变更不再启动镜像构建；未知、格式错误或重复的候选选择标记直接失败。

本轮两次 CI 只证明轻量路由和比较器的固定输入回归；没有重新执行镜像构建或 Dev/Container 全链路，不增加上表应用通过数量。剩余研究按收益排序：Dev/smoke 的构建、快照与归档重复；正式切换时的旧入口/重复定时任务收敛；候选内约 401 行禁用发布 Shell 的最终归属。层诊断枚举全部 Linux 平台，详细诊断仅检查 amd64/arm64，不能作为相同覆盖直接合并。缓存与预装工具镜像需先确认上游更新语义并测量收益，暂不新增维护面。

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
| `scripts/ci/compare_image_snapshot.py` | Dev/smoke 共用的纯 JSON 比较器；保留 UNKNOWN、缺失/不可观察及版本/配置差异语义，不访问 Registry、不执行发布 |

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

用户已授权候选推送、非发布测试、读取日志和迭代修正；尚未授权正式发布、密钥操作或旧入口退役。

用户本轮追加授权完整 52 组合及 Dev/Container 验收。`acceptance`（push 标记 `[gpt-acceptance]`）从配置生成全量矩阵，并以 `vlmcsd:latest` 三架构运行 Dev 和 Container 路径；`dev-verify` / `container-verify` 可定向选择一个配置目标。结果与未通过项见上表；不能预先计为通过。

候选 `WORKFLOW_READ_ONLY=true` 拒绝生产、容器发布和 Dev 晋升路由。Dev 仅运行本地构建、比较及归档，Release 创建/上传已从该构建步骤移除；晋升、外部 Registry 登录/推送、README 推送及 Release 发布步骤硬禁用。Container 构建启用后同样保留逐步骤发布禁用。这里描述的是执行门禁，候选 YAML 的全局 token 权限仍为用户既定的 `write-all`；验收 Jobs 仅请求 `contents: read`。

普通 push 默认 `validate`，也可显式使用 `[gpt-validate]`；代表性完整验证需手动选 `verification` 或使用 `[gpt-verification]`，全量仍为 `[gpt-acceptance]`。保留 `[gpt-retest:APP:TAG]`、`[gpt-dev:APP:TAG]`、`[gpt-container:APP:TAG]` 等既有定向路由，每次 push 仅接受一个标记。retest 支持逗号分隔的多个 `APP:TAG`，逐项从配置验证，拒绝重复或未知目标。全量验收拒绝目标筛选，不能用子集冒充全部。每个组合上传含 SHA、平台、阶段和退出码的证据；Dev/Container 归档只上传 Actions Artifact。定向重测不同 SHA 的历史成功不能替代同一 SHA 的全量通过。

正式 Dev 仅 `execution_route=dev` + `dev_mode=preflight` 是已验收的非发布预检；`auto` / `build` / `promote-*` 可能创建 Release 或推送 Docker Hub/GHCR，不能当作 dry run。检查、构建、镜像内测试、发布是不同验收等级；报告必须给出 Commit、Run、实际范围、跳过项及限制。

待办顺序：按约八成标准收尾非发布阶段，保留上表应用失败待办，优先推进工作流精简与可维护性；核对未选路由、外部调用方、触发器、权限和回滚方案；正式发布、Dev 晋升及旧入口退役仍须在相应授权后推进，再同步两个图检查器。Dev/Container 的代表性非发布验收已通过，不重复列为未完成；全量应用修复留待后续，不再要求先达到 52/52。当前生产与独立监控的重复定时触发仍存在。

已知事项：`novnc` 与 `novnc_alpine` 共享 `grinch27/novnc:latest`，不可静默改标签。历史应用构建失败需重新读取对应 SHA 的最新日志，不沿用旧成功/失败数字。保留 `application/.example/build/` 两份模板及 `application/ffmpeg/build/docker-ffmpeg.dockerfile` 上游参考。

## 历史资料

先前五份研究/迁移文档、历史 Run、已删除文件及其恢复链接统一保存在 [精简前 AGENTS 固定快照](https://github.com/Grinch27/docker-builder/blob/95bb3fac6a42409192c15f942d5212c5369943f1/AGENTS.md)。通过该提交读取或恢复原文；不再在现行规范中重复过时阶段描述。历史记录仅用于追溯，不构成当前发布或删除授权。回退用普通 revert，不强推分支历史。
