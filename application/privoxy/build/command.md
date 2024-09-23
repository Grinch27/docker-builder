# Privoxy 配置参数 - 根据原始配置文档进行补充修正markdown表格

## 7. HTTPS INSPECTION - HTTPS 检查参数

| 参数名 | 默认值 | 示例 | 描述 |
|-|-|-|-|
| `ca-directory` | `./CA` | `ca-directory /usr/local/etc/privoxy/CA` | 指定 CA 密钥、CA 证书和受信任 CA 文件的目录。权限应仅允许 Privoxy 和 Privoxy 管理员访问该目录。 |
| `ca-cert-file` | `cacert.crt` | `ca-cert-file root.crt` | 指定 CA 证书文件（`.crt` 格式）。Privoxy 客户端应导入该证书以验证生成的证书。 |
| `ca-key-file` | `cakey.pem` | `ca-key-file cakey.pem` | 指定 CA 密钥文件（`.pem` 格式）。访问密钥应仅限于 Privoxy。 |
| `ca-password` | 空字符串 | `ca-password swordfish` | CA 密钥文件的密码。注意密码会显示在 CGI 页面上，因此不要重复使用重要密码。 |
| `certificate-directory` | `./certs` | `certificate-directory /usr/local/var/privoxy/certs` | 指定用于保存生成的密钥和证书的目录。Privoxy 管理员应监控目录大小或确保有足够的空间。 |
| `cipher-list` | 无 | `cipher-list ALL:!EXPORT:!aNULL:!RC4` | 指定用于 TLS 握手的加密套件列表。指定不常见的加密套件列表会使指纹识别更容易。 |
| `trusted-cas-file` | `trustedCAs.pem` | `trusted-cas-file trusted_cas_file.pem` | 指定受信任的 CA 文件（`.pem` 格式）。可以从 https://curl.se/ca/cacert.pem 下载示例文件。 |

## 8. WINDOWS GUI OPTIONS - Windows GUI 选项

| 参数名 | 默认值 | 示例 | 描述 |
|-|-|-|-|
| `activity-animation` | 1 | `activity-animation 1` | 如果设置为 1，当 Privoxy 活动时图标将动画化。要关闭动画，请设置为 0。 |
| `log-messages` | 1 | `log-messages 1` | 如果设置为 1，Privoxy 将日志消息复制到控制台窗口。日志详细信息取决于 debug 指令。 |
| `log-buffer-size` | 1 | `log-buffer-size 1` | 如果设置为 1，日志缓冲区的大小将限制为 `log-max-lines`。警告：设置为 0 会导致缓冲区无限增长并耗尽所有内存。 |
| `log-max-lines` | 200 | `log-max-lines 200` | 日志缓冲区中保存的最大行数。 |
| `log-highlight-messages` | 1 | `log-highlight-messages 1` | 如果设置为 1，Privoxy 将以粗体字体突出显示日志消息的部分内容。 |
| `log-font-name` | 无 | `log-font-name Comic Sans MS` | 控制台窗口中使用的字体。 |
| `log-font-size` | 8 | `log-font-size 8` | 控制台窗口中使用的字体大小。 |
| `show-on-task-bar` | 0 | `show-on-task-bar 0` | 控制 Privoxy 最小化时是否在任务栏上显示图标。 |
| `close-button-minimizes` | 1 | `close-button-minimizes 1` | 如果设置为 1，Windows 关闭按钮将最小化 Privoxy 而不是关闭程序（使用文件菜单中的退出选项关闭）。 |
| `hide-console` | 无 | `hide-console` | 如果使用此选项，Privoxy 将断开并隐藏命令控制台。 |