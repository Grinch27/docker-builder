# AGENTS.md — Docker Builder

<!--
Repository: Grinch27/docker-builder
Part I: common GitHub Actions standards adapted from Grinch27/openwrt-compiler/AGENTS.md.
Part II-A: repository-specific instructions.
Part II-B: previous AGENTS.md, preserved verbatim.
This deployment changes only AGENTS.md; it does not authorize workflow or source modification.
-->

# Part I — GitHub Actions 通用规范（统一维护）

<!-- BEGIN: NEW WORKFLOW RULES -->
<!-- COMMON_RULES_VERSION: 1.0.0 -->
<!-- COMMON_RULES_SOURCE: Grinch27/github-actions/docs/agents/part-i.md -->

## 1. 适用范围与基本原则

本部分用于规范本项目及未来可复用的 GitHub Actions 工作流设计。

### 1.1 基本原则

- GitHub Actions 工作流分为 Non-container 和 Container 两种路线。
- 所有新项目原则上先实现 Non-container 基础路线。
- 基础路线稳定后，才开展以追新为目的的 Container 路线。
- 所有远程 Action 的 `uses` 引用必须采用经过探测的 `main` 或 `master` 分支。
- 所有适用工作流必须使用统一的 `runner-image` Job。
- 其他普通 Ubuntu Runner Job 必须使用 `needs.runner-image.outputs.RUNNER_IMAGE`。
- 工作流语法必须符合 GitHub 官方文档。
- 优先使用 `Grinch27/github-actions` 中已有的共享 Actions。
- 不因追求简化、统一或追新而破坏已经验证的构建功能。
- 不擅自修改已有的权限、私有数据处理、构建或发布边界。

### 1.2 规范层级

本文件分为两部分：

- Part I：通用 GitHub Actions 工作流规范。
- Part II：各仓库独立维护的项目专属约束（不参与同步）。

两部分相互独立，但在实际执行时共同生效。

通用工作流规范不能覆盖项目专属的安全、隐私、设备操作和授权限制。

如果两部分存在实质冲突，应先报告并确认，不得自行忽略其中一部分。

---

## 2. GitHub Actions 双路线规范

### 2.1 Non-container — 基础路线

参考文件：

[Grinch27/openwrt-compiler/build-openwrt.yml](https://github.com/Grinch27/openwrt-compiler/blob/main/.github/workflows/build-openwrt.yml)（跨仓库基础路线参考）

所有新项目原则上先使用 Non-container 构建路线。

主要特征：

- 直接使用 GitHub-hosted Ubuntu Runner。
- 在 Runner 上安装所需软件包与工具链。
- 在 Runner 上完成源码获取、构建和验证。
- 使用共享 Actions 管理通用环境。
- 使用动态 Runner Image 解析机制。
- 保留必要的构建阶段、错误状态和验证证据。

Non-container 是项目最初的开发和调试路线。

只有经过实际构建验证，才能将其视为稳定基础。

不得仅凭 YAML 语法检查、单元测试或部分 Job 成功，就认定完整构建路线已经稳定。

### 2.2 Container — 进阶路线

参考文件：

[Grinch27/uboot-mtk-compiler/uboot_allinone.yml](https://github.com/Grinch27/uboot-mtk-compiler/blob/main/.github/workflows/uboot_allinone.yml)（跨仓库 Container 路线参考）

重点参考该文件的前 200 行。

重点学习：

1. Workflow 顶层配置。
2. `run-name`。
3. `permissions`。
4. `defaults`。
5. 顶层 `env`。
6. `runner-image` Job。
7. `toolchain` Job。
8. `needs` 与 `outputs`。
9. `container`。
10. YAML Anchors 与 Aliases。
11. Job 环境变量与共享 Action 的组织方式。

Container 路线的主要目的是：

- 使用更新的 Ubuntu 容器环境。
- 探索更新的 GCC、Clang、JDK 等工具链。
- 隔离宿主 Runner 与构建环境。
- 减少宿主 Runner 预装软件带来的影响。
- 在保证构建正确性的基础上研究维护优化。

优先参考 GitHub Actions 原生 Job Container：

```yaml
jobs:
  build:
    needs: runner-image
    runs-on: ${{ needs.runner-image.outputs.RUNNER_IMAGE }}
    container:
      image: ubuntu:devel
```

`ubuntu:devel` 只是追新路线的参考示例，不是所有项目必须采用的镜像。

容器发行版和工具链版本必须结合实际项目兼容性决定。

使用 `docker run` 手动运行构建容器时，需要与 Job 级 `container:` 区分。

不得无条件复制参考项目中的 `--privileged`、Docker Socket 挂载、宿主设备挂载或安全隔离关闭参数。

### 2.3 路线开发顺序

标准开发顺序：

```text
Non-container
    |
    v
完成基础构建
    |
    v
实际验证
    |
    v
形成稳定基线
    |
    v
Container
    |
    v
探索新环境与新工具链
    |
    v
构建与兼容性验证
```

Container 路线出现失败时，必须区分：

- 源码自身问题。
- 构建脚本问题。
- Runner 环境变化。
- 容器环境变化。
- 工具链版本变化。
- 工作流配置问题。

已经采用 Container 的现有项目不因本规范而自动重构。

是否补建 Non-container 路线、是否迁移为原生 Job Container，必须作为单独任务研究和批准。

---

## 3. GitHub Actions uses 引用规范

### 3.1 强制使用 main/master

所有远程 GitHub Action 的 `steps[*].uses` 必须使用 `main` 或 `master` 分支。

禁止：

- 固定 Commit SHA。
- 固定版本 Tag。
- `@v1`、`@v2`、`@v3`、`@v4`、`@v5` 等版本引用。
- 未经探测的分支引用。

正确示例：

```yaml
- name: Checkout
  uses: actions/checkout@main

- name: Upload Artifact
  uses: actions/upload-artifact@main

- name: Resolve runner-image
  uses: Grinch27/github-actions/.github/actions/resolve-runner-image@main
```

### 3.2 一次性分支探测

每次引入一个新的远程 Action 时：

1. 检查仓库是否存在。
2. 检查其默认分支。
3. 探测 `main` 和 `master` 是否存在。
4. 检查实际 Action 入口文件。
5. 检查 Action 输入、输出和运行条件。
6. 选择有效的默认分支引用。

选择规则：

- 默认分支为 `main`：使用 `@main`。
- 默认分支为 `master`：使用 `@master`。
- 两者都存在：以仓库默认分支为准。
- 均不可用：停止自动生成并报告。
- 探测失败：不得猜测。

分支探测在编写时执行一次。

正常工作流运行时，不必重复查询默认分支。

### 3.3 引用边界

本规则适用于远程 GitHub Action 的 `steps[*].uses`。

以下形式分别处理：

- 本地 Action：`uses: ./...`，不需要远程分支引用。
- Reusable Workflow：`jobs.<job_id>.uses`，需要额外核对调用语法和运行限制。
- `docker://` Action：不具备 `@main/@master` 形式，暂不自动套用分支规则。

遇到不能直接使用 `main/master` 的依赖，不得静默改用固定版本。

必须报告实际限制和可行替代方案。

### 3.4 动态依赖风险

`main/master` 是动态引用，会随上游分支更新。

因此：

- 必须核对 Action 来源。
- 不得未经批准扩大 Token 或 Secrets 权限。
- 上游接口或行为变化后，应重新执行相关验证。
- 不得将动态引用理解为依赖内容不可变。
- 如果动态依赖带来不可接受的安全或兼容性风险，应报告冲突并停止相关变更。

本规则是用户明确选择的追新策略。

---

## 4. Runner Image 统一解析规范

### 4.1 必须使用共享 Action

所有适用的 GitHub Actions 工作流必须配置：

`Grinch27/github-actions/.github/actions/resolve-runner-image@main`

标准实现：

```yaml
jobs:
  runner-image:
    name: ubuntu-latest - runner-image
    runs-on: ubuntu-latest
    outputs:
      RUNNER_IMAGE: ${{ steps.resolve-runner-image.outputs.RUNNER_IMAGE }}
    steps:
      - name: Resolve runner-image
        id: resolve-runner-image
        uses: Grinch27/github-actions/.github/actions/resolve-runner-image@main
```

### 4.2 其他 Job 必须依赖 runner-image

标准实现：

```yaml
jobs:
  build:
    needs: runner-image
    runs-on: ${{ needs.runner-image.outputs.RUNNER_IMAGE }}
```

存在多个依赖时：

```yaml
jobs:
  build:
    needs:
      - runner-image
      - toolchain
    runs-on: ${{ needs.runner-image.outputs.RUNNER_IMAGE }}
```

要求：

- `runner-image` 必须输出 `RUNNER_IMAGE`。
- 普通 Ubuntu Runner Job 必须包含 `needs: runner-image`。
- 后续 Job 必须从 `needs.runner-image.outputs.RUNNER_IMAGE` 获取 Runner。
- 不允许在后续普通 Job 中重复硬编码 Ubuntu Runner 标签。

### 4.3 引导 Job 例外

`runner-image` Job 自身允许使用：

```yaml
runs-on: ubuntu-latest
```

因为解析 Action 必须先在一个 Runner 上运行。

不得让 `runner-image` Job 依赖自己的输出。

### 4.4 特殊工作流

Reusable Workflow 的调用 Job 不直接支持 `runs-on`。

对于不支持普通 `runs-on` 结构的 Job，需要依据官方语法单独处理。

不得为了满足形式统一而生成无效 YAML。

### 4.5 Runner 与 Container 区分

- `runs-on`：GitHub Actions Job 的宿主 Runner。
- `container.image`：运行该 Job 的容器镜像。

动态 Runner 解析不意味着 Container 镜像必须使用相同版本的 Ubuntu。

---

## 5. GitHub Actions 工作流整体风格

### 5.1 顶层结构

优先采用如下组织顺序：

```yaml
name:

# GitHub Actions workflow syntax reference:
# https://docs.github.com/zh/actions/reference/workflows-and-actions/workflow-syntax
# https://docs.github.com/zh/actions/reference/workflows-and-actions/metadata-syntax#runs-for-composite-actions
# https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations#yaml-anchors-and-aliases

on:

run-name:

permissions:

defaults:

env:

jobs:
```

可以根据实际需要添加：

- `concurrency`。
- Job 输出。
- Container 配置。
- Matrix。
- 其他 GitHub Actions 官方支持的字段。

不为了形式完整而强行添加无用途的配置。

### 5.2 环境变量

优先在顶层 `env` 中存放多个 Job 共用的环境变量。

参考：

```yaml
defaults:
  run:
    shell: bash

env:
  DEBIAN_FRONTEND: noninteractive
  DEBCONF_NONINTERACTIVE_SEEN: "true"
  APT_LISTCHANGES_FRONTEND: none
  NEEDRESTART_MODE: a
  FORCE_UNSAFE_CONFIGURE: "1"
  TZ: Etc/UTC
  LANG: C.UTF-8
  LC_ALL: C.UTF-8
  GIT_TERMINAL_PROMPT: "0"
```

该配置仅为参考集合。

各项目应依据实际需求决定保留哪些变量。

不得将 `FORCE_UNSAFE_CONFIGURE` 等可能影响构建行为的配置作为无条件默认值。

### 5.3 YAML Anchors 与 Aliases

对于多个 Job 重复使用的 Container 配置，优先评估 YAML Anchors。

参考：

```yaml
jobs:
  toolchain:
    needs: runner-image
    runs-on: ${{ needs.runner-image.outputs.RUNNER_IMAGE }}
    container:
      image: &container_image ubuntu:devel

  build:
    needs:
      - runner-image
      - toolchain
    runs-on: ${{ needs.runner-image.outputs.RUNNER_IMAGE }}
    container:
      image: *container_image
```

对于适合复用的 `options`、`volumes` 等，也可以采用同样方式。

YAML Anchors 应用于消除真正重复的配置，不得损害可读性或兼容性。

### 5.4 共享 Actions

优先检查：

`Grinch27/github-actions`

重点复用实际已经存在并经过核验的共享 Actions。

包括但不限于：

- `resolve-runner-image`
- `resolve-toolchain-version`
- `run-sudo`
- `env-toolchain`
- `env-indocker`

不得仅根据名称假定 Action 存在或具有某种功能。

调用之前必须阅读实际的 `action.yml` 或 `action.yaml`，检查输入、输出和运行要求。

### 5.5 权限与安全

`permissions` 根据当前项目既定授权确定。

不得仅因为参考工作流使用 `write-all`，便擅自扩大其他项目的工作流权限。

现有已授权权限不因本次规范制定而自动改变。

---

## 6. 技术文档

GitHub Actions 工作流语法：

https://docs.github.com/zh/actions/reference/workflows-and-actions/workflow-syntax

GitHub Actions Composite Action 元数据语法：

https://docs.github.com/zh/actions/reference/workflows-and-actions/metadata-syntax#runs-for-composite-actions

GitHub Actions YAML Anchors 与 Aliases：

https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations#yaml-anchors-and-aliases

要求：

- 修改工作流时，优先检查官方文档。
- 不推测 GitHub Actions 不支持的语法。
- 不把参考工作流的历史写法当成官方强制规范。
- 对语法、表达式作用域和 Job 依赖进行静态验证。
- 静态检查不能替代真实工作流运行。

---

## 7. 实施与授权边界

本规范仅定义工作流设计与执行边界；是否实际修改或部署由具体任务授权决定。

未经当前任务明确授权，不自动执行：

- 工作流重构。
- Non-container 路线补建。
- Container 路线迁移。
- 依赖升级。
- Action 引用替换。
- Runner 配置修改。
- 源码修改。
- 超出当前任务范围的 Git Commit 或 Push。
- GitHub Actions 工作流触发。

新的规则用于指导后续明确授权的修改任务。

不能因为当前仓库存在与新规范不一致的代码，就自动进行迁移或删除。

<!-- END: NEW WORKFLOW RULES -->

---

# Part II — Docker Builder 项目专属约束

<!-- BEGIN: PROJECT-SPECIFIC RULES -->

## 1. 原有维护约束优先

本项目的既有 `AGENTS.md` 在下方 **Part II-B** 逐字保留（以本次部署前的 `main` 为基准）。它包含真实工作流接口、`README.md` 唯一配置源、测试与非发布边界、镜像归档验收及历史运行证据。修改前必须完整阅读该部分及相关源码。

Part I 是面向未来设计的通用规范；不得据此自动恢复已经退休的 Dev、非 Container 或旧发布路径，不得擅自重建第二套构建入口。与现存实现不一致之处，需先提供符合用户授权的独立迁移方案，不得改写 Part II-B 的历史事实以掩盖差异。

## 2. 已确认工作流和配置源

当前源树包含 `.github/workflows/gpt_dev.yml` 与 `.github/workflows/download_artifact.yml`。当前核心是单一 Container 构建路线；它作为**既有实现**保留，不代表已经按照 Non-container → Container 顺序重新验收。

`README.md` 应用表、`scripts/ci/` 业务脚本与 `tests/ci/` 测试是本仓库关键维护入口。不得把参考工程中的 `build-openwrt.yml` 或 U-Boot 编译方案误认为本仓库正在使用的工作流。

项目针对 Docker/OCI 镜像构建、版本探测、平台校验、对比、离线导出及本地 Registry；不得将镜像构建成功与 Docker Hub/GHCR 发布成功混为一谈。

## 3. 不可突破的边界

既有 `AGENTS.md` 中的非发布要求优先：不新增 Docker Hub/GHCR 登录与推送、Release、Dev 晋升、自动 README 提交或权限扩张。本次只部署说明文档，不变更真实构建、监控、导出、测试与发布逻辑。

既有临时 Registry、Docker Socket、容器权限、单 Target/全平台策略、版本一致性校验、tar/xz/分卷完整性检查，只能在独立授权与回归验证下调整。构建并非生产发布；历史 CI 绿色或旧 SHA 验收不能作为当前 SHA 的完整证明。

<!-- END: DOCKER-BUILDER PROJECT RULES -->

### Part II-B — 原有 AGENTS.md 原文保留

<!-- BEGIN: ORIGINAL AGENTS.MD — VERBATIM -->

# AGENTS.md — docker-builder
适用于根目录及所有子目录。先检查当前源码、远端 main、工作区及对应 Run；历史成功不能替代当前 SHA 的验证。

## 当前实现（2026-10-18）
保留 `.github/workflows/gpt_dev.yml`、`.github/workflows/download_artifact.yml` 两个工作流。核心只有 **9 个普通 Job、一个 Container 构建实现、一个公开输入 targets**。9 个业务脚本保留在 `scripts/ci/`，8 个集中测试文件保留在 `tests/ci/`。

| 事件 | 行为 |
|---|---|
| main 普通 push | 配置、单元测试和规划检查；不构建 |
| 每日 01:00 UTC schedule | 24 个应用版本监控、生成 Artifact；不构建，不推送 README |
| workflow_dispatch | 所选 Target 的全部配置平台经过 Container 构建、Test、比较、导出和压缩验收；固定基础镜像诊断每次运行一次 |

targets 默认/空值为 vlmcsd。接受 `app`、`app:tag`、逗号列表或 `all`；多 Tag 应用必须指定 Tag，重复/未知/显式空 Tag 直接失败。`all` 当前为 **24 应用、30 Target、52 Target/平台组合**，全部直接进入 Container 矩阵，不替换成代表应用。矩阵仅携带实际构建配置，已删除无人消费的 target_id 字段。按 30 个 Target 展开 Job，每个 Job 包含该 Target 的平台列表；单 Target 失败即停止后续步骤，其他 Target 因 fail-fast=false 继续，未执行的平台不计为通过。没有单架构或其他构建路线开关；提交消息不参与规划。

```bash
gh workflow run gpt_dev.yml --ref main -f targets=vlmcsd
gh workflow run gpt_dev.yml --ref main -f targets=samba:alpine
gh workflow run gpt_dev.yml --ref main -f targets=aria2,samba:alpine,vlmcsd,runner:actions-slim
gh workflow run gpt_dev.yml --ref main -f targets=all
```

全量命令仅说明接口，不表示已授权或已经执行新一轮全量。现行版本不接受旧 verify、路线、任意 JSON 矩阵、自由环境变量、诊断 profile、版本/修订覆盖参数，不提供旧 CLI 回退。Catalog 的矩阵工具只返回应用及 Tag，不再输出失效的 runner/custom-env 字段。

## 构建与验收契约
- Container 使用 `ubuntu:devel`，经顶层 CONTAINER_IMAGE → runner-image 输出引用；运行在动态解析的 Runner 上。
- 明确使用 **宿主 Docker socket**。容器只安装必需工具、Docker CLI/Buildx，不安装 Engine、不重启 daemon、不混用 DIND，不安装 OpenWrt/GCC/JDK 工具链。Docker 客户端包使用受支持的 noble 源；Job 镜像仍为 devel。
- 记录实际 DockerRootDir、daemon 所在文件系统和产物目录磁盘。需要 Docker API 1.49+（逐平台 inspect；save 要求 1.48+）；不宣称 Docker 数据已迁移到其他磁盘。大应用磁盘容量仍须实测。
- 每 Target 一次 Buildx 多平台构建，仅推送 **127.0.0.1:5000 本地 Registry**。每个平台分别拉取、核对实际 OS/架构/Variant、执行 README Test、比较和导出。
- Test 用 `/bin/sh` 覆盖 ENTRYPOINT，复制整个 test 目录并执行原始 test.sh；保留业务脚本退出码。该检查不代表服务默认启动、VPN、GUI 或 GPU 实机验收。
- 每个平台 Meta-app 必须产生有效版本；缺失探针直接报错，不能伪造版本。Test 必须成功并产生有效实际版本，与选定的构建版本及镜像 version Label 完全一致后才允许比较/导出；所有配置平台的实际版本须一致。
- Docker Hub/GHCR 均匿名读取原 OCI/平台配置；比较器保留 SAME、CHANGED、MISSING、UNOBSERVABLE、UNKNOWN 语义，UNKNOWN 失败。不因缺少匿名权限伪装成镜像不存在。
- `docker image save --platform` 后先核对归档内的平台、单一 manifest 和层文件，再记录原 tar SHA256。压缩和分卷后，门禁检查完整平台集合、全部文件、连续分卷、xz 解码完整性及解压流与原 tar 的 SHA256；不在磁盘重建大型 tar。
- 产物为 `container-acceptance-APP-TAG-aATTEMPT`，包含 output、metadata、离线 release.md。普通归档保持 APP_TAG_VERSION_PLATFORM.tar.xz 格式；版本中的文件名不安全字符替换为连字符，原始版本保存在元数据。分卷使用现有 file-split/*.partNNN，校验和记录相对路径。
- 压缩前只清理本次 Buildx、本地 Registry 和构建镜像；不作宿主全局 prune。Artifact 保留 **1 天**，所有矩阵 max-parallel **10**，不设置 timeout-minutes。
- 固定诊断为 debian:latest、ubuntu:latest、alpine:latest、debian:sid、ubuntu:devel：枚举全部 Linux 平台层，详细检查 amd64/arm64（10 项），聚合及最终门禁检查证据完整；不按每个应用重复运行。

## 非发布边界及授权
本轮用户已批准 Container 单实现迁移、删除旧实现/参数/消息选择器及提交 main。其他旧 build/check、Dev、逐平台独立构建和重复 Meta-app Job 已退休；禁用的外部发布实现已删除，纯 OCI 比较保留。
不进行 Docker Hub/GHCR 登录或推送、GitHub Release 发布、Dev 晋升、自动 README 提交、密钥操作或生产变更。全局 `permissions: write-all` 是用户既定规范，构建 Job 显式 contents: read；权限声明不能作为发布授权。
独立下载工具保留 URL 下载和指定平台镜像拉取/导出两种模式，不构建或推送镜像。已知 URL 下载的 aria2→curl 回退后仍受失败状态影响，待单独处理；本轮不改该工具的业务行为。
Git 历史保留旧实现；回退用普通 revert，不强推或重置共享历史。改动前检查外部消费者，现有 Artifact/CLI 的退休不代表外部调用者已全部迁移。

## 唯一配置与源码
README.md 末尾 Applications 表格是唯一维护源，保留 **Application / JSON / Build / Meta-app / Test** 五列，以及 app-summary/app-json/app-build/app-meta/app-test 起止标记和 HTML 实体编码。
JSON.config 人工维护，monitor 记录由监控更新；Meta-app/Test 是完整可执行 Shell 源码，禁止摘要、占位符、预期版本替代。Build 列由配置生成，不手工维护第二套命令。
当前 24 份 Test、23 份 Meta-app；FFmpeg 缺少 Meta-app 是真实缺失状态。生成脚本仅在临时 Actions 工作区恢复，不提交重复副本：
```bash
python3 scripts/ci/materialize_test_hooks.py --app APP --kind meta
python3 scripts/ci/materialize_test_hooks.py --app APP --kind test
```
每个 Target 使用独立、非符号链接的 `application/APP/TAG.Dockerfile`，上下文为 `application/APP/`。仅缺失 Tag 默认 latest，显式空值/null、非法 Tag、缺失文件直接失败；禁止共享、回退或配置第二个 Dockerfile 路径。build_tag 决定文件，不能将版本号或发布 Tag 当作新 Target。
保持 README 配置、监控记录、Meta-app/Test、平台及应用源码。改写 README 前比较全部配置和脚本并验证幂等，不用生成命令掩盖源码丢失。已知 novnc 与 novnc_alpine 共享 grinch27/novnc:latest，不静默改名。

## 业务脚本
| 文件 | 职责 |
|---|---|
| catalog.py | 唯一表格配置、严格 Tag/文件解析、维护与展示生成 |
| workflow_plan.py | 按事件和 targets 生成 Container/共享诊断或监控矩阵，不读取提交消息 |
| monitor_state.py | 语义监控记录、README 临时渲染和报告；monitor-state schema_version=2；不生成构建矩阵，不接受 force/build-targets 参数 |
| materialize_test_hooks.py | 从 README 恢复完整 Meta-app/Test，不执行 Shell，拒绝异内容/符号链接覆盖 |
| build-image.sh | 单一 Buildx 本地 Registry 导出；拒绝非本地 Registry，不保留 load 模式 |
| compare_image_snapshot.py | 纯 JSON OCI 比较，无网络和发布行为 |
| verify_image_archive.py | Docker-save 平台检查，以及整组压缩/分卷字节完整性检查；不提取归档 |
| inspect-image-platform.sh | 固定平台 Skopeo 元数据及 Artifact |
| aggregate-layer-artifacts.py | 聚合 OCI 层证据，不访问 Registry |

新增/修改脚本在文件头说明需求、未知项、后续研究、优化、风险和验证。修复依据真实失败证据；不得删矩阵项、忽略退出码或弱化 Test 换取绿色状态。步骤键顺序 name > id > if > uses > with > env > working-directory > shell > run；Actions 保持核验过的 main/master 引用。

## 验证与证据
```bash
python3 scripts/ci/catalog.py validate
python3 scripts/ci/catalog.py summary --check
python3 scripts/ci/catalog.py matrix --kind version
python3 scripts/ci/catalog.py matrix --kind build
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/ci" python3 -m unittest discover -s tests/ci -p 'test_*.py' -v
actionlint -shellcheck='' -pyflakes='' -ignore 'anchor "container_(options|volumes)" is defined but not used' .github/workflows/gpt_dev.yml .github/workflows/download_artifact.yml
git diff --check
```
actionlint v1.7.12 仅需精确豁免独立下载工具两个既有未使用锚点提示。新核心不再需要 queue/常量 false 豁免。未安装或未执行 shellcheck/pyflakes 时明确说明，不计作通过。
本轮基线 f83e6bf。本地已通过 108 项测试和 9 Job 图检查；覆盖实际 Container Test/导出 Shell 的成功及失败、平台变体、UNKNOWN、Meta-app 管道失败、最终步骤门禁、真实 tar/xz/分卷的损坏/缺失/额外文件/校验和不匹配。移除旧路线专属测试不计为新能力丢失。
本地没有 Docker，不宣称进行了真实镜像构建。新 Container-only、全量 52 组合和监控远端执行均以对应 SHA/Run 为准；普通 push 成功只证明轻量验证。

迁移代码 ce5fb46 / [39091135553](https://github.com/Grinch27/docker-builder/actions/runs/39091135553) 与收尾 9a3d00f / [39091332259](https://github.com/Grinch27/docker-builder/actions/runs/39091332259)：远端轻量 CI 均 success，2 成功/7 跳过。已读最终 Job 117568565889 日志确认 108 项测试、9 Job 图及 build=false/monitor=false；另有全部 30 个 Target 的真实 Bash 构建参数夹具通过（未调用 Docker），不视为真实 Container 构建通过。

## 再检查与修正（2026-10-18，基线 9a3d00f）
原始 Shell 夹具确认两个缺口：监控探针打印版本后退出 7 仍记录 success；Test 实测 2.0 仍能导出带 1.0 版本名的归档。本轮修正监控显式失败状态、完整探针日志及实际版本/镜像 Label/构建版本一致性；不修改应用源码，不追加应用专项修复。
监控分别记录 materialize_failed、meta_app_missing、pull_failed、run_failed、copy_failed、probe_failed、version_invalid；失败时 version=unknown，部分输出不作为有效版本。每个应用上传独立 probe-APP.log，不复制宿主环境，不保留失效的自定义环境及无消费者步骤输出。监控 Job 成功表示记录及 Artifact 完成，不表示全部应用探针成功或镜像构建成功。
新增真实 Shell 回归覆盖上述失败、缺失/未知/CR/NUL 版本、平台选择和 actual/label 版本不匹配；本地共 112 项测试通过，9 个业务脚本、8 个测试文件、9 Job 和全部 30/52 配置保留。最终提交的 CI 必须另读对应 Run；本轮没有真实 Docker 构建或全量运行。浏览器登录请求曾被拒绝，不自动重试登录。

## 历史验收与冻结应用
约八成可构建标准继续有效：失败只记录原因和状态，不追加冻结应用修复，不删除其配置，不重跑全部矩阵或继续等待耗时应用，除非用户另行指定。
- 历史全量 faefe3f / [39028192731](https://github.com/Grinch27/docker-builder/actions/runs/39028192731)：41/52；后续跨 SHA 定向证据为 44/52、20/24 应用，不代表同一提交全量成功。
- Tag 目录迁移 c7ad230 / [39045898957](https://github.com/Grinch27/docker-builder/actions/runs/39045898957)：已确认 42/52（80.8%）组合、24/30 Target 全平台通过；完整应用口径 18/24。8 失败、2 耗时项按用户要求本轮不验收，不计为通过。
- 历史 Dev 046df23 / [39079220995](https://github.com/Grinch27/docker-builder/actions/runs/39079220995) 及 Container dc9ff58 / [39079222968](https://github.com/Grinch27/docker-builder/actions/runs/39079222968)：vlmcsd 三平台成功。该 Container 日志 DockerRootDir=/var/lib/docker；不能证明旧 /builder/docker-data 配置生效，也不能替代本轮验收。
- 两输入基线 f83e6bf / [39083789076](https://github.com/Grinch27/docker-builder/actions/runs/39083789076)：121 测试、2 成功/13 跳过，只是轻量验证。

| 应用 | 已知原因及状态 |
|---|---|
| expressvpn | 四平台下载地址为空；冻结待处理 |
| ffmpeg | 历史 Mesa once_flag/call_once 冲突；缺少 Meta-app 将阻断新 Container 前置探针；冻结，本轮不复测 |
| stable-diffusion-webui-amdgpu | 历史 Python/scikit-image 编译问题，后续 Runner 根盘耗尽；耗时项本轮不验收 |
| ttrss | 缺 docker-entrypoint.sh、src/wait-for.sh、ttrss.nginx.conf、initialize.php、s6；冻结待处理，Test 也未声明实际版本 |
| novnc | 迁移轮未提取到下载 tarball_url；只记录，未重测 |
| runner:actions | 迁移轮版本提取为空导致下载 HTTP 404；只记录，未重测 |

详细迁移过程、旧路线、历史文档及完整文件映射保留在 [迁移前 AGENTS 固定快照](https://github.com/Grinch27/docker-builder/blob/f83e6bf1ca49c93bb958c2176ca60ca05ef9838e/AGENTS.md)，历史说明不构成现行接口或新授权。
<!-- END: ORIGINAL AGENTS.MD — VERBATIM -->
