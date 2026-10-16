# docker-builder

GitHub Actions 构建、检测与发布 Docker 镜像。 / Build, test and publish Docker images.

`app-config` JSON 中的 `config` 是镜像构建配置的唯一来源；`monitor.records` 保存监控历史。下方 Applications 表格是配置与监控结果的展示视图，**其中 Meta-app 与 Test 两列的 Shell 代码则是各自脚本的唯一来源**。

## Workflow / 工作流

- [Production](.github/workflows/docker_allinone.yml)：定时构建与发布；手动 Dev 路由调用 [Dev](.github/workflows/docker_allinone_dev.yml)。
- [Monitor](.github/workflows/monitor-images.yml)：版本监控；[GPT Smoke](.github/workflows/docker_allinone_gpt.yml)：非发布测试；[Diagnostics](.github/workflows/diagnostics.yml)：诊断。

## Maintenance / 维护

人工维护 `config`，自动化仅更新 `monitor.records`。修改配置后重新生成表格；必须保留 `app-summary`、`app-config` 以及各个 `app-meta`/`app-test` 标记。

```bash
python3 scripts/ci/catalog.py validate
python3 scripts/ci/catalog.py summary --write
python3 scripts/ci/catalog.py summary --check
python3 -m unittest discover -s scripts/ci -p 'test_catalog.py' -v
python3 -m unittest discover -s scripts/ci -p 'test_materialize_test_hooks.py' -v
```

**注意：** `novnc` 与 `novnc_alpine` 共享 `grinch27/novnc:latest`。版本探针成功不代表镜像已经发布。

参考：[仓库维护规范、应用目录与历史记录](AGENTS.md)。

## Machine-readable configuration / Actions 配置

<details>
<summary>展开配置与监控 JSON / Configuration and monitor JSON</summary>

<!-- app-config:start -->
```json
{
  "schema_version": 2,
  "config": {
    "schema_version": 1,
    "apps": {
      "adguardvpn-cli": {
        "repository": "grinch27/adguardvpn-cli",
        "base_image": "alpine:latest",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "keep",
        "targets": [
          {
            "tag": "nightly",
            "dockerfile": "Dockerfile",
            "build_arg": "update_channel=nightly"
          },
          {
            "tag": "beta",
            "dockerfile": "Dockerfile",
            "build_arg": "update_channel=beta"
          },
          {
            "tag": "release",
            "dockerfile": "Dockerfile",
            "build_arg": "update_channel=release"
          }
        ]
      },
      "aria2": {
        "repository": "grinch27/aria2",
        "base_image": "alpine:latest",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "baidunetdisk": {
        "repository": "grinch27/baidunetdisk",
        "base_image": "debian:stable-slim",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "dev",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "cloudflare-warp": {
        "repository": "grinch27/cloudflare-warp",
        "base_image": "ubuntu:devel",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "curl": {
        "repository": "grinch27/curl",
        "base_image": "alpine:edge",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "keep",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "dnscrypt-proxy": {
        "repository": "grinch27/dnscrypt-proxy",
        "base_image": "alpine:edge",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "doh-nosni": {
        "repository": "grinch27/doh-nosni",
        "base_image": "debian:sid-slim",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "expressvpn": {
        "repository": "grinch27/expressvpn",
        "base_image": "debian:stable-slim",
        "platforms": [
          "linux/amd64",
          "linux/arm64",
          "linux/386",
          "linux/arm/v7"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "ffmpeg": {
        "repository": "grinch27/ffmpeg",
        "base_image": "ubuntu:devel",
        "platforms": [
          "linux/amd64"
        ],
        "tag_policy": "none",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "nordvpn": {
        "repository": "grinch27/nordvpn",
        "base_image": "debian:stable-slim",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "novnc": {
        "repository": "grinch27/novnc",
        "base_image": "debian:stable-slim",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "novnc_alpine": {
        "repository": "grinch27/novnc",
        "base_image": "alpine:latest",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "none",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "openwrt": {
        "repository": "grinch27/openwrt",
        "base_image": "ubuntu:devel",
        "platforms": [
          "linux/amd64"
        ],
        "tag_policy": "none",
        "targets": [
          {
            "tag": "main",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "privoxy": {
        "repository": "grinch27/privoxy",
        "base_image": "alpine:latest",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "protonvpn": {
        "repository": "grinch27/protonvpn",
        "base_image": "debian:stable-slim",
        "platforms": [
          "linux/amd64"
        ],
        "tag_policy": "none",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "runner": {
        "repository": "grinch27/runner",
        "base_image": "debian:testing-slim",
        "platforms": [
          "linux/amd64"
        ],
        "tag_policy": "none",
        "targets": [
          {
            "tag": "dev",
            "dockerfile": "Dockerfile"
          },
          {
            "tag": "slim",
            "dockerfile": "slim.Dockerfile"
          },
          {
            "tag": "actions",
            "dockerfile": "actions.Dockerfile"
          },
          {
            "tag": "actions-slim",
            "dockerfile": "actions-slim.Dockerfile"
          }
        ]
      },
      "samba": {
        "repository": "grinch27/samba",
        "base_image": "debian:testing-slim",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          },
          {
            "tag": "alpine",
            "dockerfile": "alpine.Dockerfile",
            "base_image": "alpine:latest"
          }
        ]
      },
      "sdnext": {
        "repository": "grinch27/sdnext",
        "base_image": "rocm/dev-ubuntu-24.04",
        "platforms": [
          "linux/amd64"
        ],
        "tag_policy": "strip_channel_and_spaces",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "sdnext-dev": {
        "repository": "grinch27/sdnext",
        "base_image": "ubuntu:24.04",
        "platforms": [
          "linux/amd64"
        ],
        "tag_policy": "strip_channel_and_spaces",
        "targets": [
          {
            "tag": "dev",
            "dockerfile": "Dockerfile",
            "build_arg": "therock_version=7.11.0,therock_release_type=stable,therock_amdgpu_family=gfx110X-all"
          }
        ]
      },
      "squid": {
        "repository": "grinch27/squid",
        "base_image": "alpine:latest",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "stable-diffusion-webui-amdgpu": {
        "repository": "grinch27/stable-diffusion-webui-amdgpu",
        "base_image": "rocm/dev-ubuntu-24.04",
        "platforms": [
          "linux/amd64"
        ],
        "tag_policy": "strip_channel_and_spaces",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "steamcmd": {
        "repository": "grinch27/steamcmd",
        "base_image": "debian:testing-slim",
        "platforms": [
          "linux/amd64"
        ],
        "tag_policy": "none",
        "targets": [
          {
            "tag": "dev",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "ttrss": {
        "repository": "grinch27/ttrss",
        "base_image": "alpine:latest",
        "platforms": [
          "linux/amd64",
          "linux/arm64"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      },
      "vlmcsd": {
        "repository": "grinch27/vlmcsd",
        "base_image": "alpine:latest",
        "platforms": [
          "linux/amd64",
          "linux/arm64",
          "linux/386"
        ],
        "tag_policy": "strip_channel",
        "targets": [
          {
            "tag": "latest",
            "dockerfile": "Dockerfile"
          }
        ]
      }
    }
  },
  "monitor": {
    "records": [
      {
        "app_branch": "adguardvpn-cli",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "alpine:latest",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/adguardvpn-cli",
        "status": "success",
        "tag_repo": "latest",
        "version": "unknown"
      },
      {
        "app_branch": "aria2",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "alpine:latest",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/aria2",
        "status": "success",
        "tag_repo": "latest",
        "version": "1.37.0"
      },
      {
        "app_branch": "baidunetdisk",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "debian:stable-slim",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/baidunetdisk",
        "status": "success",
        "tag_repo": "latest",
        "version": "4.17.7"
      },
      {
        "app_branch": "cloudflare-warp",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "ubuntu:devel",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/cloudflare-warp",
        "status": "success",
        "tag_repo": "latest",
        "version": "unknown"
      },
      {
        "app_branch": "curl",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "alpine:edge",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/curl",
        "status": "success",
        "tag_repo": "latest",
        "version": "unknown"
      },
      {
        "app_branch": "dnscrypt-proxy",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "alpine:edge",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/dnscrypt-proxy",
        "status": "success",
        "tag_repo": "latest",
        "version": "2.1.18"
      },
      {
        "app_branch": "doh-nosni",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "debian:sid-slim",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/doh-nosni",
        "status": "success",
        "tag_repo": "latest",
        "version": "unknown"
      },
      {
        "app_branch": "expressvpn",
        "arch_branch": "linux/amd64,linux/arm64,linux/386,linux/arm/v7",
        "base_image": "debian:stable-slim",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/expressvpn",
        "status": "success",
        "tag_repo": "latest",
        "version": "unknown"
      },
      {
        "app_branch": "ffmpeg",
        "arch_branch": "linux/amd64",
        "base_image": "ubuntu:devel",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/ffmpeg",
        "status": "meta_app_missing",
        "tag_repo": "latest",
        "version": "unknown"
      },
      {
        "app_branch": "nordvpn",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "debian:stable-slim",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/nordvpn",
        "status": "success",
        "tag_repo": "latest",
        "version": "5.4.1"
      },
      {
        "app_branch": "novnc",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "debian:stable-slim",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/novnc",
        "status": "success",
        "tag_repo": "latest",
        "version": "1.7.0"
      },
      {
        "app_branch": "novnc_alpine",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "alpine:latest",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/novnc",
        "status": "success",
        "tag_repo": "latest",
        "version": "unknown"
      },
      {
        "app_branch": "openwrt",
        "arch_branch": "linux/amd64",
        "base_image": "ubuntu:devel",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/openwrt",
        "status": "success",
        "tag_repo": "latest",
        "version": "unknown"
      },
      {
        "app_branch": "privoxy",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "alpine:latest",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/privoxy",
        "status": "success",
        "tag_repo": "latest",
        "version": "4.0.0"
      },
      {
        "app_branch": "protonvpn",
        "arch_branch": "linux/amd64",
        "base_image": "debian:stable-slim",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/protonvpn",
        "status": "success",
        "tag_repo": "latest",
        "version": "1.0.8"
      },
      {
        "app_branch": "runner",
        "arch_branch": "linux/amd64",
        "base_image": "debian:testing-slim",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/runner",
        "status": "success",
        "tag_repo": "latest",
        "version": "unknown"
      },
      {
        "app_branch": "samba",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "debian:testing-slim",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/samba",
        "status": "success",
        "tag_repo": "latest",
        "version": "4.25.0"
      },
      {
        "app_branch": "sdnext",
        "arch_branch": "linux/amd64",
        "base_image": "rocm/dev-ubuntu-24.04",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/sdnext",
        "status": "success",
        "tag_repo": "latest",
        "version": "7.2"
      },
      {
        "app_branch": "sdnext-dev",
        "arch_branch": "linux/amd64",
        "base_image": "ubuntu:24.04",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/sdnext",
        "status": "success",
        "tag_repo": "latest",
        "version": "7.11"
      },
      {
        "app_branch": "squid",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "alpine:latest",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/squid",
        "status": "success",
        "tag_repo": "latest",
        "version": "7.6-VCS"
      },
      {
        "app_branch": "stable-diffusion-webui-amdgpu",
        "arch_branch": "linux/amd64",
        "base_image": "rocm/dev-ubuntu-24.04",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/stable-diffusion-webui-amdgpu",
        "status": "success",
        "tag_repo": "latest",
        "version": "7.2"
      },
      {
        "app_branch": "steamcmd",
        "arch_branch": "linux/amd64",
        "base_image": "debian:testing-slim",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/steamcmd",
        "status": "success",
        "tag_repo": "latest",
        "version": "unknown"
      },
      {
        "app_branch": "ttrss",
        "arch_branch": "linux/amd64,linux/arm64",
        "base_image": "alpine:latest",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/ttrss",
        "status": "success",
        "tag_repo": "latest",
        "version": "1113-5-g70e0357"
      },
      {
        "app_branch": "vlmcsd",
        "arch_branch": "linux/amd64,linux/arm64,linux/386",
        "base_image": "alpine:latest",
        "platform_used": "linux/amd64",
        "repo_dockerhub": "grinch27/vlmcsd",
        "status": "success",
        "tag_repo": "latest",
        "version": "1113-5-g70e0357"
      }
    ]
  }
}
```
<!-- app-config:end -->

</details>

## Applications / 应用清单

<!-- app-summary:start -->
**24 applications / 30 build targets** (generated from configuration below).

| Application | Registry repository | Tags | Platforms | Base image | Dockerfiles | Detected version | Probe status | Meta-app | Test |
|---|---|---|---|---|---|---|---|---|---|
| [adguardvpn-cli](application/adguardvpn-cli/) | `grinch27/adguardvpn-cli` | `nightly`, `beta`, `release` | `amd64`, `arm64` | `alpine:latest` | `Dockerfile` | `unknown` | `success` | <!-- app-meta:adguardvpn-cli:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apk update -q&#10;apk add --no-cache -q \&#10;    ca-certificates \&#10;    curl \&#10;    gpg \&#10;    jq \&#10;    grep \&#10;    sed&#10;# ----- System info -----&#10;cpu='x86_64'&#10;case "$(uname --machine)" in&#10;    'x86_64'&#124;'amd64') cpu='x86_64' ;;&#10;    'aarch64'&#124;'arm64') cpu='aarch64' ;;&#10;    'armv7l') cpu='armv7' ;;&#10;    # 'mips') cpu=$(hexdump -o &lt;&lt;&lt;I &#124; awk '{print substr($2, 6, 1)}' &#124; grep -q 1 &amp;&amp; echo 'mipsel' &#124;&#124; echo 'mips') ;;&#10;    *) echo "Unsupported CPU architecture: $(uname --machine)" ; exit 1 ;;&#10;esac&#10;&#10;set -x&#10;&#10;# ----- install.sh -----&#10;# export URL_SH="https://raw.githubusercontent.com/AdguardTeam/AdGuardVPNCLI/master/scripts/${tag_repo}/install.sh"&#10;# export FILE_SH="/install.sh"&#10;# curl -fsSL ${URL_SH} -o ${FILE_SH}&#10;&#10;# version=$(grep -oP "version='.*?'" ${FILE_SH} &#124; head -1)&#10;# version=$(echo ${version} &#124; awk -F"'" '{print $2}')&#10;# echo "version=${version}"&#10;&#10;# ----- load build_arg -----&#10;env_build="/tmp/build.env"&#10;env_docker="/etc/environment"&#10;flag_split=","&#10;# while IFS="${flag_split}" read -r line; do&#10;#     key=$(echo "$line" &#124; cut -d '=' -f1)&#10;#     value=$(echo "$line" &#124; cut -d '=' -f2-)&#10;#     if [ -n "$key" ] &amp;&amp; [ -n "$value" ]; then&#10;#         echo "$key=$value" &gt;&gt; /etc/environment&#10;#     fi&#10;# done &lt; ${env_build}&#10;cat ${env_build}&#10;build_arg=$(grep "^build_arg=" ${env_build} &#124; sed -r "s&#124;^build_arg=['\"](.*)['\"]&#124;\1&#124;")&#10;echo ${build_arg}&#10;echo "${build_arg}" &#124; tr "${flag_split}" '\n' &#124; while IFS='=' read -r key value; do&#10;    if [ -n "$key" ] &amp;&amp; [ -n "$value" ]; then&#10;        echo "$key=$value" &gt;&gt; ${env_docker};&#10;    fi;&#10;done&#10;echo -e "----- check ${env_docker} -----"&#10;cat ${env_docker}&#10;&#10;set -a&#10;. ${env_docker}&#10;unset build_arg&#10;set +a&#10;printenv&#10;&#10;tag_target=${update_channel}&#10;# https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/tags&#10;tag_download=$(curl -s "https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/tags" &#124; \&#10;    jq -r --arg tag_target "$tag_target" '.[] &#124; select(.name &#124; contains($tag_target)) &#124; .name' &#124; head -n 1)&#10;# # https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/releases/tags/v1.0.0&#10;# URL_download=$(curl -s "https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/releases/tags/${tag_download}" &#124; \&#10;#     jq -r --arg cpu "$cpu" '.assets[] &#124; select(.name &#124; contains($cpu)) &#124; .browser_download_url' &#124; head -n 1)&#10;&#10;version=${tag_download}&#10;remove_prefix="v"&#10;remove_suffix="-"&#10;version=${version##*$remove_prefix}&#10;version=${version%%$remove_suffix*}&#10;echo "version=${version}"&#10;&#10;&#10;&#10;# apk update&#10;# apk add --no-cache -q \&#10;#     ca-certificates \&#10;#     curl \&#10;#     tar \&#10;#     gpg&#10;# # install.sh&#10;# export URL_SH="https://raw.githubusercontent.com/AdguardTeam/AdGuardVPNCLI/master/scripts/${tag_repo}/install.sh"&#10;# export FILE_SH="/install.sh"&#10;# curl -fsSL ${URL_SH} -o ${FILE_SH}&#10;# sed -i 's/read -r response &lt; \/dev\/tty/response="y"/g' ${FILE_SH}&#10;# chmod +x ${FILE_SH}&#10;# sh --verbose ${FILE_SH}&#10;# rm -f ${FILE_SH}&#10;&#10;# version=$(adguardvpn-cli --version)&#10;# remove_prefix="AdGuard VPN CLI v"&#10;# version=${version##*$remove_prefix}&#10;# echo "version=${version}"&#10;</code></pre></details><!-- app-meta:adguardvpn-cli:end --> | <!-- app-test:adguardvpn-cli:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;version=$(adguardvpn-cli --version)&#10;remove_prefix="AdGuard VPN CLI v"&#10;version=${version##*$remove_prefix}&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-test:adguardvpn-cli:end --> |
| [aria2](application/aria2/) | `grinch27/aria2` | `latest` | `amd64`, `arm64` | `alpine:latest` | `Dockerfile` | `1.37.0` | `success` | <!-- app-meta:aria2:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apk update -q&#10;apk add --no-cache -q \&#10;    ca-certificates \&#10;    aria2&#10;&#10;aria2c --version&#10;version=$(aria2c --version)&#10;version=$(echo "$version" &#124; awk '/aria2 version / {print $3}')&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:aria2:end --> | <!-- app-test:aria2:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;set -eu&#10;version=$(aria2c --version &#124; awk '/^aria2 version / {print $3; exit}')&#10;if [ -z "$version" ]; then echo "Unable to determine aria2 version" &gt;&amp;2; exit 1; fi&#10;case "$version" in *[![:print:]]*) echo "Invalid image version" &gt;&amp;2; exit 1;; esac&#10;printf 'version=%s\n' "$version"&#10;</code></pre></details><!-- app-test:aria2:end --> |
| [baidunetdisk](application/baidunetdisk/) | `grinch27/baidunetdisk` | `dev` | `amd64`, `arm64` | `debian:stable-slim` | `Dockerfile` | `4.17.7` | `success` | <!-- app-meta:baidunetdisk:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;# version=$(warp-cli --version)&#10;# remove_prefix="warp-cli "&#10;# version=${version##*$remove_prefix}&#10;version="4.17.7"&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:baidunetdisk:end --> | <!-- app-test:baidunetdisk:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;# version=$(warp-cli --version)&#10;# remove_prefix="warp-cli "&#10;# version=${version##*$remove_prefix}&#10;# echo "version=${version}"&#10;sleep 10&#10;</code></pre></details><!-- app-test:baidunetdisk:end --> |
| [cloudflare-warp](application/cloudflare-warp/) | `grinch27/cloudflare-warp` | `latest` | `amd64`, `arm64` | `ubuntu:devel` | `Dockerfile` | `unknown` | `success` | <!-- app-meta:cloudflare-warp:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;export DEBIAN_FRONTEND=noninteractive&#10;apt-get update --ignore-missing&#10;apt-get install -y --no-install-recommends -qq \&#10;    ca-certificates \&#10;    gpg \&#10;    curl \&#10;    lsb-release&#10;&#10;# Add cloudflare gpg key&#10;OS_ARCH=$(dpkg --print-architecture)&#10;OS_VER=$(lsb_release -cs)&#10;curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg &#124; gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg&#10;echo "deb [arch=${OS_ARCH} signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ ${OS_VER} main" &gt; /etc/apt/sources.list.d/cloudflare-client.list&#10;apt-get update&#10;&#10;# # Install cloudflare-warp&#10;# apt-get install -y \&#10;#     cloudflare-warp&#10;&#10;# # Clean pre-install&#10;# apt-get purge --autoremove -y \&#10;#     curl \&#10;#     lsb-release&#10;    &#10;# # Clean apt&#10;# apt-get clean&#10;# rm -rf /var/lib/apt/lists/*&#10;# rm -rf /var/log/*.log&#10;# unset DEBIAN_FRONTEND&#10;&#10;# # ENTRYPOINT startapp.sh&#10;# echo "#!/bin/sh\nservice dbus start\n/bin/warp-svc\nwarp-cli disconnect --accept-tos" &gt; /startapp.sh&#10;# chmod +x /startapp.sh&#10;&#10;# version=$(warp-cli --version)&#10;# remove_prefix="warp-cli "&#10;# version=${version##*$remove_prefix}&#10;# echo "version=${version}"&#10;&#10;version=$(apt-cache madison cloudflare-warp &#124; awk -F '&#124;' '{print $2}' &#124; tr -d ' ' &#124; head -n 1)&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:cloudflare-warp:end --> | <!-- app-test:cloudflare-warp:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;version=$(warp-cli --version)&#10;remove_prefix="warp-cli "&#10;version=${version##*$remove_prefix}&#10;echo "version=${version}"&#10;&#10;# (base) user@user:~$ warp-cli&#10;# CLI to the WARP service daemon&#10;&#10;# Usage: warp-cli [OPTIONS] &lt;COMMAND&gt;&#10;&#10;# Commands:&#10;#   connect               Maintain a connection whenever possible&#10;#   debug                 Debugging commands&#10;#   disconnect            Disconnect the client&#10;#   dns                   Configure DNS settings&#10;#   environment           Configure the WARP Client's compliance environment&#10;#   mdm                   MDM configs&#10;#   mode                  Set the client's general operating mode&#10;#   override              Allow temporary overrides of administrative settings&#10;#   proxy                 Configure proxy mode settings&#10;#   registration          Registration settings&#10;#   connector             Register a WARP Connector&#10;#   settings              Show or alter general application settings&#10;#   status                Return the current connection status&#10;#   target                Manage targets&#10;#   trusted               Configure trusted networks where the client will be automatically disabled (Consumer only)&#10;#   tunnel                Configure tunnel settings&#10;#   vnet                  Get or specify connected virtual network&#10;#   generate-completions  Generate completions for a given shell and print to stdout&#10;#   stats                 Display statistics for Cloudflare WARP&#10;#   certs                 Print all account certificates installed on the device to stdout&#10;#   help                  Print this message or the help of the given subcommand(s)&#10;&#10;# Options:&#10;#   -l, --listen       Listen for status changes and DNS logs (if enabled)&#10;#       --accept-tos   Accept the Terms of Service agreement&#10;#   -v, --verbose...   Enable verbose output. Multiple "v"s adds more verbosity&#10;#   -j, --json         Pretty print output as json&#10;#       --no-paginate  Disable automatic pagination&#10;#       --no-ansi      Disable ANSI characters in standard outputs&#10;#   -h, --help         Print help (see more with '--help')&#10;#   -V, --version      Print version&#10;</code></pre></details><!-- app-test:cloudflare-warp:end --> |
| [curl](application/curl/) | `grinch27/curl` | `latest` | `amd64`, `arm64` | `alpine:edge` | `Dockerfile` | `unknown` | `success` | <!-- app-meta:curl:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apt-get update --ignore-missing -y -qq&#10;apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \&#10;  ca-certificates \&#10;  curl&#10;&#10;version=$(curl --version &#124; awk 'NR==1 {print $2}')&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:curl:end --> | <!-- app-test:curl:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;set -eu&#10;version=$(curl --version &#124; awk 'NR==1 {print $2; exit}')&#10;if [ -z "$version" ]; then echo "Unable to determine curl version" &gt;&amp;2; exit 1; fi&#10;case "$version" in *[![:print:]]*) echo "Invalid image version" &gt;&amp;2; exit 1;; esac&#10;printf 'version=%s\n' "$version"&#10;</code></pre></details><!-- app-test:curl:end --> |
| [dnscrypt-proxy](application/dnscrypt-proxy/) | `grinch27/dnscrypt-proxy` | `latest` | `amd64`, `arm64` | `alpine:edge` | `Dockerfile` | `2.1.18` | `success` | <!-- app-meta:dnscrypt-proxy:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# 获取当前目录&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apk update -q&#10;apk add --no-cache -q \&#10;    ca-certificates \&#10;    dnscrypt-proxy&#10;&#10;version=$(dnscrypt-proxy -version)&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:dnscrypt-proxy:end --> | <!-- app-test:dnscrypt-proxy:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;set -eu&#10;version=$(dnscrypt-proxy -version &#124; awk 'NR==1 {print; exit}')&#10;if [ -z "$version" ]; then echo "Unable to determine dnscrypt-proxy version" &gt;&amp;2; exit 1; fi&#10;case "$version" in *[![:print:]]*) echo "Invalid image version" &gt;&amp;2; exit 1;; esac&#10;printf 'version=%s\n' "$version"&#10;</code></pre></details><!-- app-test:dnscrypt-proxy:end --> |
| [doh-nosni](application/doh-nosni/) | `grinch27/doh-nosni` | `latest` | `amd64`, `arm64` | `debian:sid-slim` | `Dockerfile` | `unknown` | `success` | <!-- app-meta:doh-nosni:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;&#10;# apt-get update --ignore-missing -y -qq&#10;# apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \&#10;# 	ca-certificates \&#10;# 	samba&#10;&#10;# # Version 4.20.6&#10;# # 4.21.3-Debian-4.21.3+dfsg-6+b1&#10;# version=$(smbd --version)&#10;# # version=$(echo "$version" &#124; awk '/Version/ {print $2}')&#10;# # echo "version=${version}"&#10;&#10;# remove_prefix="Version "&#10;# remove_suffix="-Debian"&#10;# version=${version##*$remove_prefix}&#10;# version=${version%%$remove_suffix*}&#10;# echo "version=${version}"&#10;</code></pre></details><!-- app-meta:doh-nosni:end --> | <!-- app-test:doh-nosni:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;set -eu&#10;version=$(dnscrypt-proxy -version &#124; awk 'NR==1 {print; exit}')&#10;if [ -z "$version" ]; then echo "Unable to determine doh-nosni version" &gt;&amp;2; exit 1; fi&#10;case "$version" in *[![:print:]]*) echo "Invalid image version" &gt;&amp;2; exit 1;; esac&#10;printf 'version=%s\n' "$version"&#10;</code></pre></details><!-- app-test:doh-nosni:end --> |
| [expressvpn](application/expressvpn/) | `grinch27/expressvpn` | `latest` | `amd64`, `arm64`, `386`, `arm/v7` | `debian:stable-slim` | `Dockerfile` | `unknown` | `success` | <!-- app-meta:expressvpn:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apt-get update --ignore-missing -qq&#10;apt-get install -y --no-install-recommends -qq \&#10;    ca-certificates \&#10;    curl&#10;    # gpg \&#10;    # lsb-release&#10;    # systemd \&#10;    # expect \&#10;    # iproute2 \&#10;    # jq \&#10;    # iputils-ping&#10;    # html-xml-utils \&#10;    # tidy&#10;    # dbus&#10;    # nano&#10;    # man&#10;    # iptables&#10;    # nftables&#10;    # vim&#10;    # sudo&#10;    # procps&#10;&#10;# ===== Download deb file =====&#10;OS_ARCH=$(dpkg --print-architecture)&#10;# OS_VER=$(lsb_release -cs)&#10;export URL_HTML="https://www.expressvpn.works/latest"&#10;export FILE_HTML="/latest.html"&#10;curl -fsSL ${URL_HTML} -o ${FILE_HTML}&#10;&#10;# ----- select download url -----&#10;echo "OS_ARCH=${OS_ARCH}"&#10;if [ "${OS_ARCH}" = "amd64" ]; then&#10;    URL_DOWNLOAD=$(grep -oP 'https://.*?/clients/linux/.*?_amd64.deb' ${FILE_HTML} &#124; head -1);&#10;elif [ "${OS_ARCH}" = "i386" ]; then&#10;    URL_DOWNLOAD=$(grep -oP 'https://.*?/clients/linux/.*?_i386.deb' ${FILE_HTML} &#124; head -1);&#10;elif echo "${OS_ARCH}" &#124; grep -q "arm"; then&#10;    URL_DOWNLOAD=$(grep -oP 'https://.*?/clients/linux/.*?_armhf.deb' ${FILE_HTML} &#124; head -1);&#10;else&#10;    echo "Unsupported architecture: ${OS_ARCH}"&#10;    exit 1&#10;fi&#10;echo "URL_DOWNLOAD=${URL_DOWNLOAD}"&#10;&#10;version=$(basename ${URL_DOWNLOAD} &#124; awk -F'_' '{print $2}' &#124; awk -F'-' '{print $1}')&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:expressvpn:end --> | <!-- app-test:expressvpn:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;expressvpn --version&#10;&#10;version=$(expressvpn --version)&#10;remove_prefix="expressvpn version "&#10;remove_suffix=" ("&#10;version=${version##*$remove_prefix}&#10;version=${version%%$remove_suffix*}&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-test:expressvpn:end --> |
| [ffmpeg](application/ffmpeg/) | `grinch27/ffmpeg` | `latest` | `amd64` | `ubuntu:devel` | `Dockerfile` | `unknown` | `meta_app_missing` | <!-- app-meta:ffmpeg:missing -->— | <!-- app-test:ffmpeg:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apt list --installed&#10;dpkg-query -Wf '${Installed-Size}\t${Package}\n' &#124; sort -n&#10;&#10;# dpkg -L app&#10;&#10;# version=$(app --version)&#10;# remove_prefix="app "&#10;# version=${version##*$remove_prefix}&#10;# echo "version=${version}"&#10;</code></pre></details><!-- app-test:ffmpeg:end --> |
| [nordvpn](application/nordvpn/) | `grinch27/nordvpn` | `latest` | `amd64`, `arm64` | `debian:stable-slim` | `Dockerfile` | `5.4.1` | `success` | <!-- app-meta:nordvpn:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;export DEBIAN_FRONTEND=noninteractive&#10;apt-get update --ignore-missing&#10;apt-get install -y --no-install-recommends -qq \&#10;    ca-certificates \&#10;    gpg \&#10;    curl&#10;&#10;# Temporary failure resolving repo.nordvpn.com&#10;# sudo -i&#10;curl -fsSL https://repo.nordvpn.com/gpg/nordvpn_public.asc &#124; gpg --yes --dearmor --output /usr/share/keyrings/nordvpn_public.gpg&#10;echo "deb [signed-by=/usr/share/keyrings/nordvpn_public.gpg] https://repo.nordvpn.com/deb/nordvpn/debian stable main" &gt; /etc/apt/sources.list.d/nordvpn.list&#10;apt-get update&#10;&#10;# apt-get install -y \&#10;#     nordvpn&#10;&#10;# # Clean pre-install&#10;# apt-get purge --autoremove -y \&#10;#     curl \&#10;&#10;# # Clean apt&#10;# apt-get clean&#10;# rm -rf /var/lib/apt/lists/*&#10;# rm -rf /var/log/*.log&#10;# unset DEBIAN_FRONTEND&#10;&#10;# # dpkg -l&#10;# nordvpn --version&#10;&#10;version=$(apt-cache madison nordvpn &#124; awk -F '&#124;' '{print $2}' &#124; tr -d ' ' &#124; head -n 1)&#10;echo "version=${version}"&#10;&#10;# /run/nordvpn/nordvpnd.sock not found.&#10;# The NordVPN background service isn't running. Execute the "systemctl enable --now nordvpnd" command with root privileges to start the background service. If you're using NordVPN in an environment without systemd (a container, for example), use the "/etc/init.d/nordvpn start" command.&#10;</code></pre></details><!-- app-meta:nordvpn:end --> | <!-- app-test:nordvpn:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;version=$(nordvpn --version)&#10;remove_prefix="NordVPN Version "&#10;version=${version##*$remove_prefix}&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-test:nordvpn:end --> |
| [novnc](application/novnc/) | `grinch27/novnc` | `latest` | `amd64`, `arm64` | `debian:stable-slim` | `Dockerfile` | `1.7.0` | `success` | <!-- app-meta:novnc:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;# version=$(noVNC --version)&#10;# remove_prefix="noVNC "&#10;# version=${version##*$remove_prefix}&#10;&#10;export DEBIAN_FRONTEND=noninteractive&#10;apt-get update --ignore-missing&#10;apt-get install -y --no-install-recommends -qq \&#10;    ca-certificates \&#10;    gpg \&#10;    curl \&#10;    lsb-release&#10;URL_noVNC=$(curl -s https://api.github.com/repos/novnc/noVNC/releases/latest &#124; grep 'tarball_url' &#124; cut -d ':' -f 2- &#124; cut -d '"' -f 2)&#10;version=$(echo "${URL_noVNC}" &#124; awk -F/ '{print $NF}' &#124; cut -d 'v' -f 2-)&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:novnc:end --> | <!-- app-test:novnc:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;# version=$(warp-cli --version)&#10;# remove_prefix="warp-cli "&#10;# version=${version##*$remove_prefix}&#10;# echo "version=${version}"&#10;# sleep 10&#10;</code></pre></details><!-- app-test:novnc:end --> |
| [novnc_alpine](application/novnc_alpine/) | `grinch27/novnc` | `latest` | `amd64`, `arm64` | `alpine:latest` | `Dockerfile` | `unknown` | `success` | <!-- app-meta:novnc_alpine:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;# version=$(noVNC --version)&#10;# remove_prefix="noVNC "&#10;# version=${version##*$remove_prefix}&#10;&#10;export DEBIAN_FRONTEND=noninteractive&#10;apt-get update --ignore-missing&#10;apt-get install -y --no-install-recommends -qq \&#10;    ca-certificates \&#10;    gpg \&#10;    curl \&#10;    lsb-release&#10;URL_noVNC=$(curl -s https://api.github.com/repos/novnc/noVNC/releases/latest &#124; grep 'tarball_url' &#124; cut -d ':' -f 2- &#124; cut -d '"' -f 2)&#10;version=$(echo "${URL_noVNC}" &#124; awk -F/ '{print $NF}' &#124; cut -d 'v' -f 2-)&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:novnc_alpine:end --> | <!-- app-test:novnc_alpine:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;version=$(awk -F: '&#10;    $1 == "P" {package = $2}&#10;    package == "novnc" &amp;&amp; $1 == "V" {print $2; exit}&#10;    $0 == "" {package = ""}&#10;' /lib/apk/db/installed)&#10;if [ -z "${version}" ]; then&#10;    echo "Unable to determine the installed noVNC package version" &gt;&amp;2&#10;    exit 1&#10;fi&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-test:novnc_alpine:end --> |
| [openwrt](application/openwrt/) | `grinch27/openwrt` | `main` | `amd64` | `ubuntu:devel` | `Dockerfile` | `unknown` | `success` | <!-- app-meta:openwrt:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;# apt list --installed&#10;# dpkg-query -Wf '${Installed-Size}\t${Package}\n' &#124; sort -n&#10;&#10;version=""&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:openwrt:end --> | <!-- app-test:openwrt:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;if [ ! -r /etc/openwrt_release ]; then&#10;    echo "Missing OpenWrt release metadata" &gt;&amp;2&#10;    exit 1&#10;fi&#10;&#10;# shellcheck disable=SC1091&#10;. /etc/openwrt_release&#10;if [ -z "${DISTRIB_RELEASE:-}" ] &#124;&#124; [ -z "${DISTRIB_REVISION:-}" ]; then&#10;    echo "Incomplete OpenWrt release metadata" &gt;&amp;2&#10;    exit 1&#10;fi&#10;echo "version=${DISTRIB_RELEASE}-${DISTRIB_REVISION}"&#10;</code></pre></details><!-- app-test:openwrt:end --> |
| [privoxy](application/privoxy/) | `grinch27/privoxy` | `latest` | `amd64`, `arm64` | `alpine:latest` | `Dockerfile` | `4.0.0` | `success` | <!-- app-meta:privoxy:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apk update -q&#10;apk add --no-cache -q \&#10;    ca-certificates \&#10;    privoxy&#10;&#10;version=$(privoxy --version)&#10;version=$(echo "$version" &#124; awk '/Privoxy version / {print $3}')&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:privoxy:end --> | <!-- app-test:privoxy:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;set -eu&#10;version=$(privoxy --version &#124; awk '/^Privoxy version / {print $3; exit}')&#10;if [ -z "$version" ]; then echo "Unable to determine privoxy version" &gt;&amp;2; exit 1; fi&#10;case "$version" in *[![:print:]]*) echo "Invalid image version" &gt;&amp;2; exit 1;; esac&#10;printf 'version=%s\n' "$version"&#10;</code></pre></details><!-- app-test:privoxy:end --> |
| [protonvpn](application/protonvpn/) | `grinch27/protonvpn` | `latest` | `amd64` | `debian:stable-slim` | `Dockerfile` | `1.0.8` | `success` | <!-- app-meta:protonvpn:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;export DEBIAN_FRONTEND=noninteractive&#10;apt-get update --ignore-missing&#10;apt-get install -y --no-install-recommends -qq \&#10;    ca-certificates \&#10;    gpg \&#10;    curl&#10;&#10;gpg_file="/usr/share/keyrings/protonvpn_public.gpg"&#10;curl -fsSL https://repo.protonvpn.com/debian/public_key.asc &#124; gpg --yes --dearmor --output ${gpg_file}&#10;echo "deb [signed-by=${gpg_file}] https://repo.protonvpn.com/debian stable main" &gt; /etc/apt/sources.list.d/protonvpn.list&#10;apt-get update --ignore-missing -y -qq&#10;&#10;version=$(apt-cache madison protonvpn-stable-release &#124; awk -F '&#124;' '{print $2}' &#124; tr -d ' ' &#124; head -n 1)&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:protonvpn:end --> | <!-- app-test:protonvpn:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apt list --installed&#10;dpkg-query -Wf '${Installed-Size}\t${Package}\n' &#124; sort -n&#10;&#10;# dpkg -L app&#10;&#10;# version=$(app --version)&#10;# remove_prefix="app "&#10;# version=${version##*$remove_prefix}&#10;# echo "version=${version}"&#10;</code></pre></details><!-- app-test:protonvpn:end --> |
| [runner](application/runner/) | `grinch27/runner` | `dev`, `slim`, `actions`, `actions-slim` | `amd64` | `debian:testing-slim` | `Dockerfile`, `slim.Dockerfile`, `actions.Dockerfile`, `actions-slim.Dockerfile` | `unknown` | `success` | <!-- app-meta:runner:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apt list --installed&#10;dpkg-query -Wf '${Installed-Size}\t${Package}\n' &#124; sort -n&#10;&#10;version=""&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:runner:end --> | <!-- app-test:runner:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apt list --installed&#10;dpkg-query -Wf '${Installed-Size}\t${Package}\n' &#124; sort -n&#10;&#10;if [ -x /actions-runner/bin/Runner.Listener ]; then&#10;    version=$(/actions-runner/bin/Runner.Listener --version 2&gt;/dev/null &#124; awk 'NF {value=$NF} END {print value}')&#10;else&#10;    os_version=$(sed -n 's/^VERSION_CODENAME=//p' /etc/os-release &#124; tr -d '"')&#10;    gcc_version=$(gcc -dumpfullversion -dumpversion)&#10;    version="debian-${os_version}-gcc-${gcc_version}"&#10;    if command -v clang &gt;/dev/null 2&gt;&amp;1; then&#10;        clang_version=$(clang --version &#124; awk 'NR == 1 {print $4}')&#10;        version="${version}-clang-${clang_version}"&#10;    fi&#10;    if command -v cmake &gt;/dev/null 2&gt;&amp;1; then&#10;        cmake_version=$(cmake --version &#124; awk 'NR == 1 {print $3}')&#10;        version="${version}-cmake-${cmake_version}"&#10;    fi&#10;fi&#10;&#10;if [ -z "${version}" ]; then&#10;    echo "Unable to determine runner version identity" &gt;&amp;2&#10;    exit 1&#10;fi&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-test:runner:end --> |
| [samba](application/samba/) | `grinch27/samba` | `latest`, `alpine` | `amd64`, `arm64` | `debian:testing-slim` + `alpine: alpine:latest` | `Dockerfile`, `alpine.Dockerfile` | `4.25.0` | `success` | <!-- app-meta:samba:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;set -eu&#10;&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;if command -v apk &gt;/dev/null 2&gt;&amp;1; then&#10;    apk update -q&#10;    apk add --no-cache -q         ca-certificates         samba&#10;elif command -v apt-get &gt;/dev/null 2&gt;&amp;1; then&#10;    export DEBIAN_FRONTEND=noninteractive&#10;    apt-get update --ignore-missing -y -qq&#10;    apt-get install         --no-install-recommends         --no-install-suggests         --fix-missing         -y -qq         ca-certificates         samba&#10;else&#10;    echo "Unsupported package manager: neither apk nor apt-get is available." &gt;&amp;2&#10;    exit 1&#10;fi&#10;&#10;version=$(smbd --version)&#10;version=${version#Version }&#10;version=${version%%-*}&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:samba:end --> | <!-- app-test:samba:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;# Version 4.20.6&#10;# 4.21.3-Debian-4.21.3+dfsg-6+b1&#10;version=$(smbd --version)&#10;# version=$(echo "$version" &#124; awk '/Version/ {print $2}')&#10;# echo "version=${version}"&#10;&#10;remove_prefix="Version "&#10;remove_suffix="-Debian"&#10;version=${version##*$remove_prefix}&#10;version=${version%%$remove_suffix*}&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-test:samba:end --> |
| [sdnext](application/sdnext/) | `grinch27/sdnext` | `latest` | `amd64` | `rocm/dev-ubuntu-24.04` | `Dockerfile` | `7.2` | `success` | <!-- app-meta:sdnext:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;set -eu&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;version=""&#10;&#10;if [ -n "${ROCM_VERSION:-}" ]; then&#10;  version="${ROCM_VERSION}"&#10;fi&#10;&#10;if [ -z "${version}" ] &amp;&amp; [ -f /opt/rocm/.info/version ]; then&#10;  version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version)&#10;fi&#10;&#10;if [ -z "${version}" ] &amp;&amp; [ -f /opt/rocm/.info/version-utils ]; then&#10;  version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version-utils)&#10;fi&#10;&#10;if [ -n "${version}" ]; then&#10;  version=$(echo "${version}" &#124; sed -E 's/^([0-9]+\.[0-9]+).*/\1/')&#10;fi&#10;&#10;if [ -z "${version}" ]; then&#10;  version="7.2"&#10;fi&#10;&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:sdnext:end --> | <!-- app-test:sdnext:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;set -eu&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;if [ -x /mnt/python/venv/bin/python ]; then&#10;  py_cmd=/mnt/python/venv/bin/python&#10;elif [ -x /opt/venv/bin/python ]; then&#10;  py_cmd=/opt/venv/bin/python&#10;else&#10;  py_cmd=python3&#10;fi&#10;&#10;${py_cmd} --version &#124;&#124; true&#10;&#10;${py_cmd} - &lt;&lt;'PY'&#10;try:&#10;    import torch&#10;    print(f"torch={torch.__version__}")&#10;    print(f"hip={getattr(torch.version, 'hip', 'unknown')}")&#10;    print(f"cuda_available={torch.cuda.is_available()}")&#10;except Exception as exc:&#10;    print(f"torch=unavailable ({exc})")&#10;PY&#10;&#10;if [ -x /opt/rocm/bin/rocminfo ]; then&#10;  /opt/rocm/bin/rocminfo &gt;/dev/null 2&gt;&amp;1 &#124;&#124; true&#10;fi&#10;&#10;if [ -d /app/.git ]; then&#10;  commit_id=$(git -C /app rev-parse --short HEAD &#124;&#124; true)&#10;  echo "commit=${commit_id}"&#10;fi&#10;&#10;version=""&#10;if [ -f /opt/rocm/.info/version ]; then&#10;  version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version)&#10;elif [ -f /opt/rocm/.info/version-utils ]; then&#10;  version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version-utils)&#10;fi&#10;version=$(echo "${version:-7.2}" &#124; sed -E 's/^([0-9]+\.[0-9]+).*/\1/')&#10;&#10;echo "version=rocm${version}"&#10;</code></pre></details><!-- app-test:sdnext:end --> |
| [sdnext-dev](application/sdnext-dev/) | `grinch27/sdnext` | `dev` | `amd64` | `ubuntu:24.04` | `Dockerfile` | `7.11` | `success` | <!-- app-meta:sdnext-dev:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;set -eu&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;version=""&#10;&#10;if [ -n "${ROCM_VERSION:-}" ]; then&#10;  version="${ROCM_VERSION}"&#10;fi&#10;&#10;if [ -z "${version}" ] &amp;&amp; [ -n "${THEROCK_VERSION:-}" ]; then&#10;  version="${THEROCK_VERSION}"&#10;fi&#10;&#10;if [ -z "${version}" ] &amp;&amp; [ -f /etc/therock-version ]; then&#10;  version=$(awk 'NR==1 {print $1}' /etc/therock-version)&#10;fi&#10;&#10;if [ -z "${version}" ] &amp;&amp; [ -f /opt/rocm/.info/version ]; then&#10;  version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version)&#10;fi&#10;&#10;if [ -z "${version}" ] &amp;&amp; [ -f /opt/rocm/.info/version-utils ]; then&#10;  version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version-utils)&#10;fi&#10;&#10;if [ -n "${version}" ]; then&#10;  version=$(echo "${version}" &#124; sed -E 's/^([0-9]+\.[0-9]+).*/\1/')&#10;fi&#10;&#10;if [ -z "${version}" ]; then&#10;  version="7.11"&#10;fi&#10;&#10;echo "version=${version}"</code></pre></details><!-- app-meta:sdnext-dev:end --> | <!-- app-test:sdnext-dev:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;set -eu&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;if [ -x /mnt/python/venv/bin/python ]; then&#10;  py_cmd=/mnt/python/venv/bin/python&#10;elif [ -x /opt/venv/bin/python ]; then&#10;  py_cmd=/opt/venv/bin/python&#10;else&#10;  py_cmd=python3&#10;fi&#10;&#10;${py_cmd} --version &#124;&#124; true&#10;&#10;${py_cmd} - &lt;&lt;'PY'&#10;try:&#10;    import torch&#10;    print(f"torch={torch.__version__}")&#10;    print(f"hip={getattr(torch.version, 'hip', 'unknown')}")&#10;    print(f"cuda_available={torch.cuda.is_available()}")&#10;except Exception as exc:&#10;    print(f"torch=unavailable ({exc})")&#10;PY&#10;&#10;if [ -f /etc/therock-version ]; then&#10;  therock_version=$(awk 'NR==1 {print $1}' /etc/therock-version)&#10;  echo "therock=${therock_version}"&#10;fi&#10;&#10;if [ -x /opt/rocm/bin/rocminfo ]; then&#10;  /opt/rocm/bin/rocminfo &gt;/dev/null 2&gt;&amp;1 &#124;&#124; true&#10;fi&#10;&#10;if [ -d /app/.git ]; then&#10;  commit_id=$(git -C /app rev-parse --short HEAD &#124;&#124; true)&#10;  echo "commit=${commit_id}"&#10;fi&#10;&#10;version=""&#10;if [ -n "${ROCM_VERSION:-}" ]; then&#10;  version="${ROCM_VERSION}"&#10;elif [ -n "${THEROCK_VERSION:-}" ]; then&#10;  version="${THEROCK_VERSION}"&#10;elif [ -f /etc/therock-version ]; then&#10;  version=$(awk 'NR==1 {print $1}' /etc/therock-version)&#10;elif [ -f /opt/rocm/.info/version ]; then&#10;  version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version)&#10;elif [ -f /opt/rocm/.info/version-utils ]; then&#10;  version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version-utils)&#10;fi&#10;version=$(echo "${version:-7.11}" &#124; sed -E 's/^([0-9]+\.[0-9]+).*/\1/')&#10;&#10;echo "version=rocm${version}"</code></pre></details><!-- app-test:sdnext-dev:end --> |
| [squid](application/squid/) | `grinch27/squid` | `latest` | `amd64`, `arm64` | `alpine:latest` | `Dockerfile` | `7.6-VCS` | `success` | <!-- app-meta:squid:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apk update -q&#10;apk add --no-cache -q \&#10;    ca-certificates \&#10;    squid&#10;&#10;version=$(squid --version)&#10;version=$(echo "$version" &#124; awk '/Squid Cache: Version/ {print $4}')&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:squid:end --> | <!-- app-test:squid:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;set -eu&#10;version=$(squid --version &#124; awk '/^Squid Cache: Version/ {print $4; exit}')&#10;if [ -z "$version" ]; then echo "Unable to determine squid version" &gt;&amp;2; exit 1; fi&#10;case "$version" in *[![:print:]]*) echo "Invalid image version" &gt;&amp;2; exit 1;; esac&#10;printf 'version=%s\n' "$version"&#10;</code></pre></details><!-- app-test:squid:end --> |
| [stable-diffusion-webui-amdgpu](application/stable-diffusion-webui-amdgpu/) | `grinch27/stable-diffusion-webui-amdgpu` | `latest` | `amd64` | `rocm/dev-ubuntu-24.04` | `Dockerfile` | `7.2` | `success` | <!-- app-meta:stable-diffusion-webui-amdgpu:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;set -eu&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;version=""&#10;&#10;if [ -n "${ROCM_VERSION:-}" ]; then&#10;	version="${ROCM_VERSION}"&#10;fi&#10;&#10;if [ -z "${version}" ] &amp;&amp; [ -f /opt/rocm/.info/version ]; then&#10;	version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version)&#10;fi&#10;&#10;if [ -z "${version}" ] &amp;&amp; [ -f /opt/rocm/.info/version-utils ]; then&#10;	version=$(awk 'NR==1 {print $1}' /opt/rocm/.info/version-utils)&#10;fi&#10;&#10;if [ -n "${version}" ]; then&#10;	version=$(echo "${version}" &#124; sed -E 's/^([0-9]+\.[0-9]+).*/\1/')&#10;fi&#10;&#10;if [ -z "${version}" ]; then&#10;	version="7.2"&#10;fi&#10;&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:stable-diffusion-webui-amdgpu:end --> | <!-- app-test:stable-diffusion-webui-amdgpu:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;set -eu&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;if [ -x /opt/venv/bin/python ]; then&#10;	py_cmd=/opt/venv/bin/python&#10;else&#10;	py_cmd=python3&#10;fi&#10;&#10;${py_cmd} --version&#10;&#10;${py_cmd} - &lt;&lt;'PY'&#10;import torch&#10;print(f"torch={torch.__version__}")&#10;print(f"hip={getattr(torch.version, 'hip', 'unknown')}")&#10;print(f"cuda_available={torch.cuda.is_available()}")&#10;PY&#10;&#10;if [ -x /opt/rocm/bin/rocminfo ]; then&#10;	/opt/rocm/bin/rocminfo &gt;/dev/null 2&gt;&amp;1 &#124;&#124; true&#10;fi&#10;&#10;if [ -d /opt/stable-diffusion-webui/.git ]; then&#10;	commit_id=$(git -C /opt/stable-diffusion-webui rev-parse --short HEAD)&#10;	echo "commit=${commit_id}"&#10;fi&#10;&#10;version=$(${py_cmd} - &lt;&lt;'PY'&#10;import torch&#10;hip = getattr(torch.version, "hip", "unknown")&#10;if isinstance(hip, str) and hip and hip != "unknown":&#10;		parts = hip.split(".")&#10;		hip = ".".join(parts[:2])&#10;print(f"rocm{hip}-torch{torch.__version__}")&#10;PY&#10;)&#10;&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-test:stable-diffusion-webui-amdgpu:end --> |
| [steamcmd](application/steamcmd/) | `grinch27/steamcmd` | `dev` | `amd64` | `debian:testing-slim` | `Dockerfile` | `unknown` | `success` | <!-- app-meta:steamcmd:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;version=""&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-meta:steamcmd:end --> | <!-- app-test:steamcmd:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;# version=$(warp-cli --version)&#10;# remove_prefix="warp-cli "&#10;# version=${version##*$remove_prefix}&#10;# echo "version=${version}"&#10;&#10;apt list&#10;dpkg -L steamcmd&#10;# ls -lh /home/steam/&#10;steamcmd&#10;</code></pre></details><!-- app-test:steamcmd:end --> |
| [ttrss](application/ttrss/) | `grinch27/ttrss` | `latest` | `amd64`, `arm64` | `alpine:latest` | `Dockerfile` | `1113-5-g70e0357` | `success` | <!-- app-meta:ttrss:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apk add --no-cache -q git make build-base&#10;git clone --branch master --single-branch https://github.com/Wind4/vlmcsd.git&#10;cd vlmcsd/&#10;&#10;# check repo version&#10;git describe --tags --long&#10;# svn info&#10;&#10;# make&#10;make&#10;cp bin/vlmcsd /usr/bin/vlmcsd&#10;&#10;# /usr/bin/vlmcsd -D -d&#10;vlmcsd -V&#10;&#10;version=$(vlmcsd -V)&#10;remove_prefix="vlmcsd svn"&#10;remove_suffix=", built"&#10;version=${version##*$remove_prefix}&#10;version=${version%%$remove_suffix*}&#10;echo "version=${version}"&#10;&#10;# Usage:&#10;#    /usr/bin/vlmcsd [ options ]&#10;# Where:&#10;#   -u &lt;user&gt;		set uid to &lt;user&gt;&#10;#   -g &lt;group&gt;		set gid to &lt;group&gt;&#10;#   -a &lt;csvlk&gt;=&lt;epid&gt;	use &lt;epid&gt; for &lt;csvlk&gt;&#10;#   -r 0&#124;1&#124;2		set ePID randomization level (default 1)&#10;#   -C &lt;LCID&gt;		use fixed &lt;LCID&gt; in random ePIDs&#10;#   -H &lt;build&gt;		use fixed &lt;build&gt; number in random ePIDs&#10;#   -o 0&#124;1&#124;2&#124;3		set protection level against clients with public IP addresses (default 0)&#10;#   -x &lt;level&gt;		exit if warning &lt;level&gt; reached (default 0)&#10;#   -L &lt;address&gt;[:&lt;port&gt;]	listen on IP address &lt;address&gt; with optional &lt;port&gt;&#10;#   -P &lt;port&gt;		set TCP port &lt;port&gt; for subsequent -L statements (default 1688)&#10;#   -F0, -F1		disable/enable binding to foreign IP addresses&#10;#   -m &lt;clients&gt;		Handle max. &lt;clients&gt; simultaneously (default no limit)&#10;#   -e			log to stdout&#10;#   -D			run in foreground&#10;#   -K 0&#124;1&#124;2&#124;3		set white-listing level for KMS IDs (default -K0)&#10;#   -c0, -c1		disable/enable client time checking (default -c0)&#10;#   -M0, -M1		disable/enable maintaining clients (default -M0)&#10;#   -E0, -E1		disable/enable start with empty client list (default -E0, ignored if -M0)&#10;#   -t &lt;seconds&gt;		disconnect clients after &lt;seconds&gt; of inactivity (default 30)&#10;#   -d			disconnect clients after each request&#10;#   -k			don't disconnect clients after each request (default)&#10;#   -N0, -N1		disable/enable NDR64&#10;#   -B0, -B1		disable/enable bind time feature negotiation&#10;#   -p &lt;file&gt;		write pid to &lt;file&gt;&#10;#   -i &lt;file&gt;		use config file &lt;file&gt;&#10;#   -j &lt;file&gt;		use KMS data file &lt;file&gt;&#10;#   -R &lt;interval&gt;		renew activation every &lt;interval&gt; (default 1w)&#10;#   -A &lt;interval&gt;		retry activation every &lt;interval&gt; (default 2h)&#10;#   -l syslog		log to syslog&#10;#   -l &lt;file&gt;		log to &lt;file&gt;&#10;#   -T0, -T1		disable/enable logging with time and date (default -T1)&#10;#   -v			log verbose&#10;#   -q			don't log verbose (default)&#10;#   -V			display version information and exit&#10;</code></pre></details><!-- app-meta:ttrss:end --> | <!-- app-test:ttrss:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;vlmcsd -V&#10;&#10;version=$(vlmcsd -V)&#10;remove_prefix="vlmcsd svn"&#10;remove_suffix=", built"&#10;version=${version##*$remove_prefix}&#10;version=${version%%$remove_suffix*}&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-test:ttrss:end --> |
| [vlmcsd](application/vlmcsd/) | `grinch27/vlmcsd` | `latest` | `amd64`, `arm64`, `386` | `alpine:latest` | `Dockerfile` | `1113-5-g70e0357` | `success` | <!-- app-meta:vlmcsd:start --><details><summary>Meta-app</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;apk add --no-cache -q git make build-base&#10;git clone --branch master --single-branch https://github.com/Wind4/vlmcsd.git&#10;cd vlmcsd/&#10;&#10;# check repo version&#10;git describe --tags --long&#10;# svn info&#10;&#10;# make&#10;make&#10;cp bin/vlmcsd /usr/bin/vlmcsd&#10;&#10;# /usr/bin/vlmcsd -D -d&#10;vlmcsd -V&#10;&#10;version=$(vlmcsd -V)&#10;remove_prefix="vlmcsd svn"&#10;remove_suffix=", built"&#10;version=${version##*$remove_prefix}&#10;version=${version%%$remove_suffix*}&#10;echo "version=${version}"&#10;&#10;# Usage:&#10;#    /usr/bin/vlmcsd [ options ]&#10;# Where:&#10;#   -u &lt;user&gt;		set uid to &lt;user&gt;&#10;#   -g &lt;group&gt;		set gid to &lt;group&gt;&#10;#   -a &lt;csvlk&gt;=&lt;epid&gt;	use &lt;epid&gt; for &lt;csvlk&gt;&#10;#   -r 0&#124;1&#124;2		set ePID randomization level (default 1)&#10;#   -C &lt;LCID&gt;		use fixed &lt;LCID&gt; in random ePIDs&#10;#   -H &lt;build&gt;		use fixed &lt;build&gt; number in random ePIDs&#10;#   -o 0&#124;1&#124;2&#124;3		set protection level against clients with public IP addresses (default 0)&#10;#   -x &lt;level&gt;		exit if warning &lt;level&gt; reached (default 0)&#10;#   -L &lt;address&gt;[:&lt;port&gt;]	listen on IP address &lt;address&gt; with optional &lt;port&gt;&#10;#   -P &lt;port&gt;		set TCP port &lt;port&gt; for subsequent -L statements (default 1688)&#10;#   -F0, -F1		disable/enable binding to foreign IP addresses&#10;#   -m &lt;clients&gt;		Handle max. &lt;clients&gt; simultaneously (default no limit)&#10;#   -e			log to stdout&#10;#   -D			run in foreground&#10;#   -K 0&#124;1&#124;2&#124;3		set white-listing level for KMS IDs (default -K0)&#10;#   -c0, -c1		disable/enable client time checking (default -c0)&#10;#   -M0, -M1		disable/enable maintaining clients (default -M0)&#10;#   -E0, -E1		disable/enable start with empty client list (default -E0, ignored if -M0)&#10;#   -t &lt;seconds&gt;		disconnect clients after &lt;seconds&gt; of inactivity (default 30)&#10;#   -d			disconnect clients after each request&#10;#   -k			don't disconnect clients after each request (default)&#10;#   -N0, -N1		disable/enable NDR64&#10;#   -B0, -B1		disable/enable bind time feature negotiation&#10;#   -p &lt;file&gt;		write pid to &lt;file&gt;&#10;#   -i &lt;file&gt;		use config file &lt;file&gt;&#10;#   -j &lt;file&gt;		use KMS data file &lt;file&gt;&#10;#   -R &lt;interval&gt;		renew activation every &lt;interval&gt; (default 1w)&#10;#   -A &lt;interval&gt;		retry activation every &lt;interval&gt; (default 2h)&#10;#   -l syslog		log to syslog&#10;#   -l &lt;file&gt;		log to &lt;file&gt;&#10;#   -T0, -T1		disable/enable logging with time and date (default -T1)&#10;#   -v			log verbose&#10;#   -q			don't log verbose (default)&#10;#   -V			display version information and exit&#10;</code></pre></details><!-- app-meta:vlmcsd:end --> | <!-- app-test:vlmcsd:start --><details><summary>Test</summary><pre><code>#!/bin/sh&#10;&#10;# Get current directory&#10;dir_current=$(dirname "$(readlink -f "$0")")&#10;echo "dir_current=${dir_current}"&#10;&#10;vlmcsd -V&#10;&#10;version=$(vlmcsd -V)&#10;remove_prefix="vlmcsd svn"&#10;remove_suffix=", built"&#10;version=${version##*$remove_prefix}&#10;version=${version%%$remove_suffix*}&#10;echo "version=${version}"&#10;</code></pre></details><!-- app-test:vlmcsd:end --> |
<!-- app-summary:end -->
