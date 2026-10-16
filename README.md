# docker-builder

Github Actions for Docker Image Building

## Application Configuration

This version-controlled JSON block is the application configuration source of truth. Edit it through `scripts/ci/catalog.py` or by a reviewed commit. The generated version sections below are separate run output.

<!-- app-config:start -->
```json
{
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
}
```
<!-- app-config:end -->

## Container Version Matrix

This section is maintained automatically by GitHub Actions.

<!-- markdownlint-disable MD060 -->
<!-- app-version-table:start -->
Auto-generated by .github/workflows/monitor-images.yml
Volatile run metadata is intentionally omitted; this section changes only when semantic image state changes.

| app_branch | tag_repo | repo_dockerhub | version | base_image | arch_branch | platform_used | status |
|---|---|---|---|---|---|---|---|
| adguardvpn-cli | latest | grinch27/adguardvpn-cli | unknown | alpine:latest | linux/amd64,linux/arm64 | linux/amd64 | success |
| aria2 | latest | grinch27/aria2 | 1.37.0 | alpine:latest | linux/amd64,linux/arm64 | linux/amd64 | success |
| baidunetdisk | latest | grinch27/baidunetdisk | 4.17.7 | debian:stable-slim | linux/amd64,linux/arm64 | linux/amd64 | success |
| cloudflare-warp | latest | grinch27/cloudflare-warp | unknown | ubuntu:devel | linux/amd64,linux/arm64 | linux/amd64 | success |
| curl | latest | grinch27/curl | unknown | alpine:edge | linux/amd64,linux/arm64 | linux/amd64 | success |
| dnscrypt-proxy | latest | grinch27/dnscrypt-proxy | 2.1.18 | alpine:edge | linux/amd64,linux/arm64 | linux/amd64 | success |
| doh-nosni | latest | grinch27/doh-nosni | unknown | debian:sid-slim | linux/amd64,linux/arm64 | linux/amd64 | success |
| expressvpn | latest | grinch27/expressvpn | unknown | debian:stable-slim | linux/amd64,linux/arm64,linux/386,linux/arm/v7 | linux/amd64 | success |
| ffmpeg | latest | grinch27/ffmpeg | unknown | ubuntu:devel | linux/amd64 | linux/amd64 | meta_app_missing |
| nordvpn | latest | grinch27/nordvpn | 5.4.1 | debian:stable-slim | linux/amd64,linux/arm64 | linux/amd64 | success |
| novnc | latest | grinch27/novnc | 1.7.0 | debian:stable-slim | linux/amd64,linux/arm64 | linux/amd64 | success |
| novnc_alpine | latest | grinch27/novnc | unknown | alpine:latest | linux/amd64,linux/arm64 | linux/amd64 | success |
| openwrt | latest | grinch27/openwrt | unknown | ubuntu:devel | linux/amd64 | linux/amd64 | success |
| privoxy | latest | grinch27/privoxy | 4.0.0 | alpine:latest | linux/amd64,linux/arm64 | linux/amd64 | success |
| protonvpn | latest | grinch27/protonvpn | 1.0.8 | debian:stable-slim | linux/amd64 | linux/amd64 | success |
| runner | latest | grinch27/runner | unknown | debian:testing-slim | linux/amd64 | linux/amd64 | success |
| samba | latest | grinch27/samba | 4.25.0 | debian:testing-slim | linux/amd64,linux/arm64 | linux/amd64 | success |
| sdnext | latest | grinch27/sdnext | 7.2 | rocm/dev-ubuntu-24.04 | linux/amd64 | linux/amd64 | success |
| sdnext-dev | latest | grinch27/sdnext | 7.11 | ubuntu:24.04 | linux/amd64 | linux/amd64 | success |
| squid | latest | grinch27/squid | 7.6-VCS | alpine:latest | linux/amd64,linux/arm64 | linux/amd64 | success |
| stable-diffusion-webui-amdgpu | latest | grinch27/stable-diffusion-webui-amdgpu | 7.2 | rocm/dev-ubuntu-24.04 | linux/amd64 | linux/amd64 | success |
| steamcmd | latest | grinch27/steamcmd | unknown | debian:testing-slim | linux/amd64 | linux/amd64 | success |
| ttrss | latest | grinch27/ttrss | 1113-5-g70e0357 | alpine:latest | linux/amd64,linux/arm64 | linux/amd64 | success |
| vlmcsd | latest | grinch27/vlmcsd | 1113-5-g70e0357 | alpine:latest | linux/amd64,linux/arm64,linux/386 | linux/amd64 | success |
<!-- app-version-table:end -->
<!-- markdownlint-enable MD060 -->

<!-- app-version-json:start -->
```json
[
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
```
<!-- app-version-json:end -->
