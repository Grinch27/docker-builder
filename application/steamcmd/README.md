# SteamCMD 基础镜像

`steamcmd:dev` 使用 Debian 13。构建时运行 Valve 提供的 32 位 Linux 引导包，随后使用更新得到的 64 位客户端。构建宿主以及运行 32 位 HLDS 的宿主需支持执行 32 位 x86 程序。默认账户为 `steam`，UID/GID 为 `1001:1001`。构建时可通过 `USER`、`PUID` 调整账户和 UID。SteamCMD 安装在 `$STEAMCMDDIR`，默认是 `/home/steam/steamcmd`。两种架构的 `steamclient.so` 分别通过 `$HOME/.steam/sdk32` 和 `$HOME/.steam/sdk64` 提供。

## 构建与调用

在仓库根目录运行以下命令。重建时用 `--no-cache` 重新获取上游客户端，以免复用旧的更新层。

```sh
docker build --pull --no-cache --platform linux/amd64 \
  -f application/steamcmd/dev.Dockerfile -t steamcmd:dev application/steamcmd
docker run --rm steamcmd:dev
docker run --rm --network none steamcmd:dev -inhibitbootstrap +quit
docker run --rm -it steamcmd:dev +login anonymous
```

镜像默认执行 `steamcmd +quit`。在镜像名后传入 SteamCMD 参数即可替换默认参数。派生镜像可覆盖 `ENTRYPOINT` 来启动自己的服务。更新 SteamCMD 时需要写入其安装目录和 HOME。

构建网络使用自有可信缓存时，可传入 `--build-arg STEAMCMD_MIRROR=...`。缓存根目录需提供 Valve 原始引导包 `steamcmd_linux.tar.gz`、更新清单及清单引用的文件。

## 下载服务器文件

为每个实例挂载独立的 `/data` 卷。绑定宿主目录时，确保目录对镜像账户可写。

### Counter-Strike 1.6

Valve HLDS 使用 App ID `90` 和 `cstrike` 模组。首次安装后若缺少 `hlds_run` 或 `cstrike/liblist.gam`，对同一个卷再执行一次安装并复查文件。

派生镜像的本地构建和启动方式见 [CS 1.6 说明](cs16/README.md)。

```sh
docker run --rm -v cs16-server:/data steamcmd:dev \
  +@ShutdownOnFailedCommand 1 +force_install_dir /data +login anonymous \
  +app_set_config 90 mod cstrike +app_update 90 validate +quit
```

### Squad 战术小队

专用服务器使用 App ID `403240`。2026 年 11 月查阅的 Linux depot `403242` 约为 13.5 GiB，包含 `SquadGameServer.sh` 和 `SquadGame/ServerConfig/`。更新还需留出暂存空间。部署时根据实际下载的版本检查运行库和启动日志。Offworld 对主服务器列表实行许可管理，未获许可的服务器进入 Custom Servers。

```sh
docker run --rm -v squad-server:/data steamcmd:dev \
  +@ShutdownOnFailedCommand 1 +force_install_dir /data +login anonymous \
  +app_update 403240 validate +quit
```

首次安装可使用 `validate`。日常更新可省略，避免验证时覆盖改过的原始文件。两个命令只安装服务器文件。端口、运行参数和配置由各自的派生镜像或部署配置指定。

## 参考

- [Valve SteamCMD 文档](https://developer.valvesoftware.com/wiki/SteamCMD)
- [Valve SteamCMD 64 位更新清单](https://client-update.steamstatic.com/steam_cmd_steamrt64)
- [Debian 13 的 32 位 C++ 运行库](https://packages.debian.org/trixie/lib32stdc++6)
- [HLDS App 90](https://steamdb.info/app/90/)
- [Squad Dedicated Server 与 depots](https://steamdb.info/app/403240/depots/)
- [Offworld Industries 服务器许可政策](https://www.joinsquad.com/server-licensing-and-administration-policies)
