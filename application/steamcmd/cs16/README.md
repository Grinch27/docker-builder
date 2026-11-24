# Counter-Strike 1.6

镜像继承仓库自建的 `steamcmd:dev`，运行 Valve 原版 HLDS 的 App `90`、`public` 分支和 `cstrike` 模组。启动时使用 Counter-Strike 的 `SteamAppId=10` 初始化 Steam API。默认地图为 `de_dust2`，游戏端口为 UDP `27015`。运行宿主须支持 32 位 x86 程序。

在仓库根目录构建镜像，并在本机启动一个独立的数据卷。

```sh
docker build --platform linux/amd64 -t steamcmd:dev \
  -f application/steamcmd/dev.Dockerfile application/steamcmd
docker build --platform linux/amd64 -t cs16:latest \
  -f application/steamcmd/cs16/latest.Dockerfile application/steamcmd/cs16
docker run --init --name cs16 --volume cs16-server:/data \
  --publish 127.0.0.1:27015:27015/udp cs16:latest
```

首次启动由 SteamCMD 将服务器下载到 `/data`。再次启动时复用数据。每个服务器实例使用独立数据卷。挂载本机目录时，目录需对镜像内的 `steam` 用户（默认 UID `1001`）可写。

也可以将同一 `public` 版本的完整官方服务器数据预置到 `/data`，其中 `hlds_linux`、`valve/` 和 `cstrike/` 位于卷根目录。

验收从地图加载且 UDP 查询能返回后开始计时。连续 180 秒内，容器保持运行、重启次数为零，且客户端可持续查询到地图 `de_dust2`。
