# aria2

## Usage: aria2c [OPTIONS] [URI | MAGNET | TORRENT_FILE | METALINK_FILE]

| 短参数 | 长参数 | 功能描述 | 默认值 | 可选值 |
|-|-|-|-|-|
| `-v` | `--version` | 显示 aria2c 的版本号并退出 | N/A | N/A |
| `-h` | `--help[=TAG\|KEYWORD]` | 显示帮助信息，可以根据 TAG 或 KEYWORD 显示特定帮助 | #basic | #basic, #advanced, #http, #all 等 |
| `-l` | `--log=LOG` | 指定日志文件路径，`-` 表示输出到标准输出 | N/A | `/path/to/file`, `-` |
| `-d` | `--dir=DIR` | 指定下载文件保存目录 | `/` | `/path/to/directory` |
| `-o` | `--out=FILE` | 指定下载文件名，相对于 `-d` 目录 | N/A | `/path/to/file` |
| `-s` | `--split=N` | 使用 N 个连接下载文件 | 5 | 1-* |
| N/A | `--file-allocation=METHOD` | 文件分配方式 | `prealloc` | `none`, `prealloc`, `trunc`, `falloc` |
| `-c` | `--continue[=true\|false]` | 继续未完成的下载 | `false` | `true`, `false` |
| `-j` | `--max-concurrent-downloads=N` | 设置最大并行下载数 | 5 | 1-* |
| `-x` | `--max-connection-per-server=NUM` | 每个服务器的最大连接数 | 1 | 1-16 |
| `-k` | `--min-split-size=SIZE` | 设置最小分割尺寸 | 20M | 1M-1G |
| N/A | `--ftp-user=USER` | 设置 FTP 用户名 | N/A | N/A |
| N/A | `--ftp-passwd=PASSWD` | 设置 FTP 密码 | N/A | N/A |
| N/A | `--http-user=USER` | 设置 HTTP 用户名 | N/A | N/A |
| N/A | `--http-passwd=PASSWD` | 设置 HTTP 密码 | N/A | N/A |
| N/A | `--load-cookies=FILE` | 从文件加载 cookies | N/A | `/path/to/file` |
| `-T` | `--torrent-file=TORRENT_FILE` | 指定 `.torrent` 文件路径 | N/A | `/path/to/file` |
| N/A | `--enable-dht[=true\|false]` | 启用 DHT 支持 | `true` | `true`, `false` |
| N/A | `--dht-listen-port=PORT...` | 指定 DHT 使用的 UDP 监听端口 | 6881-6999 | 1024-65535 |
| `-S` | `--show-files[=true\|false]` | 列出 `.torrent` 或 `.metalink` 文件信息 | `false` | `true`, `false` |
| `-M` | `--metalink-file=METALINK_FILE` | 指定 `.meta4` 或 `.metalink` 文件路径 | N/A | `/path/to/file`, `-` |
| N/A | `--max-overall-upload-limit=SPEED` | 设置全局上传速度限制 | 0 (不限制) | 0-* (字节/秒) |
| `-u` | `--max-upload-limit=SPEED` | 设置每个 torrent 的最大上传速度 | 0 (不限制) | 0-* (字节/秒) |
| N/A | `--max-overall-download-limit=SPEED` | 设置全局下载速度限制 | N/A | 0-* (字节/秒) |
