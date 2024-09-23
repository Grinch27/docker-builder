# Privoxy 配置参数 - 根据原始配置文档进行补充修正markdown表格

## 6. MISCELLANEOUS - 杂项参数

| 参数名 | 默认值 | 示例 | 描述 |
|-|-|-|-|
| `accept-intercepted-requests` | 0 | `accept-intercepted-requests 1` | 指定是否应将拦截的请求视为有效。如果不信任客户端并希望强制它们使用 Privoxy，请启用此选项并配置数据包过滤器以将传出的 HTTP 连接重定向到 Privoxy。 |
| `allow-cgi-request-crunching` | 0 | `allow-cgi-request-crunching 1` | 指定是否可以阻止或重定向对 Privoxy CGI 页面的请求。默认情况下，Privoxy 忽略对其 CGI 页面的阻止和重定向操作。 |
| `split-large-forms` | 0 | `split-large-forms 1` | 指定 CGI 接口是否应与有问题的 HTTP 客户端保持兼容。启用此选项会将大表单拆分为较小的表单，以避免 URL 长度限制问题。 |
| `keep-alive-timeout` | 5 | `keep-alive-timeout 300` | 指定在打开连接后多长时间（以秒为单位）不再重用连接。默认情况下，Privoxy 会在客户端连接关闭或达到指定超时时关闭与服务器的连接。 |
| `tolerate-pipelining` | 1 | `tolerate-pipelining 1` | 指定是否应处理流水线请求。默认情况下，Privoxy 会丢弃过于激进的流水线请求，迫使客户端通过新连接重新发送它们。 |
| `default-server-timeout` | 无 | `default-server-timeout 60` | 假定服务器端保持活动超时（以秒为单位），如果服务器未指定。启用此选项可以显著增加连接的重用次数，但也可能增加连接问题。 |
| `connection-sharing` | 无 | `connection-sharing 1` | 指定是否应在不同的传入连接之间共享已保持活动的传出连接。启用此选项可能会增加隐私风险和连接问题。 |
| `socket-timeout` | 300 | `socket-timeout 300` | 指定在未收到数据后套接字超时的秒数。默认值较高，建议在不使用慢速代理时减少此值。 |
| `max-client-connections` | 128 | `max-client-connections 256` | 指定将服务的最大客户端连接数。限制连接数可以防止资源耗尽，但应低于操作系统的限制。 |
| `listen-backlog` | 128 | `listen-backlog 4096` | 定义操作系统中请求的连接队列长度。如果 Privoxy 在高负载下，传入的连接可能会堆积在队列中，直到它能被处理。增加队列长度可以允许更多同时到来的连接被接受。 |
| `enable-accept-filter` | 0 | `enable-accept-filter 1` | 决定 Privoxy 是否使用 "accept filter"（接受过滤器）。接受过滤器可以减少上下文切换的次数，直到有完整的 HTTP 请求时才将新的连接传递给 Privoxy。 |
| `handle-as-empty-doc-returns-ok` | 0 | `handle-as-empty-doc-returns-ok 1` | 指定 Privoxy 为被 +handle-as-empty-document 阻止的页面返回的状态码。设置为 1 时，对被 +handle-as-empty-document 阻止的页面返回 200(OK)，对其他阻止的页面仍返回 403(Forbidden)。 |
| `enable-compression` | 0 | `enable-compression 1` | 决定 Privoxy 是否在发送给客户端之前压缩缓冲内容。如果客户端支持，Privoxy 会压缩缓冲内容后再传递。但如果 Privoxy 和客户端在同一系统上，启用压缩可能会降低性能。 |
| `compression-level` | 1 | `compression-level 9` | 指定传递给 zlib 库的压缩级别。值范围为 0 到 9，数字越高，压缩越强，但耗时越长。 |
| `client-header-order` | 无 | `client-header-order Host User-Agent Accept` | 指定在转发之前客户端头部的排序顺序。默认行为是 Privoxy 保留客户端发送的头部顺序，新添加的头部放在末尾。通过这个参数可以重新排列头部，模拟不同的用户代理。 |
| `client-specific-tag` | 无 | `client-specific-tag circumvent-blocks Overrule blocks but do not affect other actions` | 为通过 Web 界面请求的客户端设置特定的标记。允许管理员创建不同的配置文件，让用户根据需要选择某些特定的设置，如绕过特定的阻止规则等。 |
| `client-tag-lifetime` | 60 | `client-tag-lifetime 180` | 指定临时启用的标签保持启用的时间（以秒为单位）。用户可能希望仅在短时间内启用某些标签，例如绕过由于过于宽泛的 URL 模式而导致的阻止。 |
| `trust-x-forwarded-for` | 0 | `trust-x-forwarded-for 1` | 指定 Privoxy 是否应使用 X-Forwarded-For 头中指定的 IP 地址。如果客户端通过另一个代理（例如负载均衡器）访问 Privoxy，Privoxy 无法从连接中识别客户端的 IP 地址。启用此选项后，Privoxy 将使用 X-Forwarded-For 头的值作为客户端 IP 地址。 |
| `receive-buffer-size` | 5000 | `receive-buffer-size 32768` | 指定 Privoxy 用于从服务器接收数据的缓冲区大小（以字节为单位）。增加缓冲区大小会增加 Privoxy 的内存使用量，但可以减少上下文切换次数，从而降低 CPU 使用率并可能提高吞吐量。 |

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