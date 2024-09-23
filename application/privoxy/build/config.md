# Privoxy 配置参数 - 根据原始配置文档config.new进行补充修正markdown表格

## 1. LOCAL SET-UP DOCUMENTATION - 本地设置文档

| 参数名 | 默认值 | 示例 | 描述 |
|-|-|-|-|
| `user-manual` | 未设置 | `user-manual /usr/share/doc/privoxy/user-manual/` | 指定 Privoxy 用户手册的位置。未设置时，将使用 https://www.privoxy.org/version/user-manual/，其中 version 是 Privoxy 的版本。 |
| `trust-info-url` | 未设置 | `trust-info-url http://www.example.com/why_we_block.html` | 指定在用户访问未受信任页面被拒绝时显示在错误页面上的 URL。 |
| `admin-address` | 未设置 | `admin-address privoxy-admin@example.com` | 指定联系 Privoxy 管理员的电子邮件地址。未设置时，错误页面和 CGI 用户界面上不会显示电子邮件地址。 |
| `proxy-info-url` | 未设置 | `proxy-info-url http://www.example.com/proxy-service.html` | 指定有关本地 Privoxy 设置、配置或策略的文档 URL。未设置时，错误页面和 CGI 用户界面上不会显示本地文档链接。 |

## 2. CONFIGURATION AND LOG FILE LOCATIONS - 配置和日志文件位置

Privoxy 可以（通常会）使用多个文件来进行额外的配置、提供帮助和记录日志。本配置文件部分用于告知 Privoxy 如何找到这些文件。
运行 Privoxy 的用户必须对所有配置文件拥有读取权限，并对任何将被修改的文件（如日志文件和操作文件）拥有写入权限。

| 参数名 | 默认值 | 示例 | 描述 |
|-|-|-|-|
| `confdir` | `/etc/privoxy` (Unix) 或 Privoxy 安装目录 (Windows) | `confdir /etc/privoxy` | 指定其他配置文件所在的目录。 |
| `templdir` | 未设置 | `templdir /path/to/templates` | 指定加载模板的备用目录。如果未设置，模板将假定位于 confdir/template 中。 |
| `temporary-directory` | 未设置 | `temporary-directory /tmp` | 指定 Privoxy 可以创建临时文件的目录。如果未设置，将不会创建临时文件，外部过滤器将无法工作。 |
| `logdir` | `/var/log/privoxy` (Unix) 或 Privoxy 安装目录 (Windows) | `logdir /var/log/privoxy` | 指定所有日志记录的目录（即日志文件所在的位置）。 |
| `actionsfile` | `match-all.action`, `default.action`, `user.action` | `actionsfile match-all.action` | 指定要使用的动作文件。可以使用多次此语句，推荐使用多个动作文件。 |
| `filterfile` | `default.filter` (Unix) 或 `default.filter.txt` (Windows) | `filterfile default.filter` | 指定要使用的过滤文件。可以使用多次此语句。 |
| `logfile` | 未设置 | `logfile privoxy.log` | 指定要使用的日志文件。如果未设置，将不会写入日志文件。 |
| `trustfile` | 未设置 | `trustfile trust` | 指定要使用的信任文件。如果未设置，整个信任机制将被禁用。 |

## 3. DEBUGGING - 调试参数

这些选项主要在追踪问题时有用。请注意，在调试时，您可能还需要使用 --no-daemon 命令行选项来启动 Privoxy。

| 参数名 | 默认值 | 示例 | 描述 |
|-|-|-|-|
| `debug` | 0 | `debug 1` | 指定记录哪些信息的关键值。可用的调试级别包括：1（记录每个请求的目标），2（显示每个连接状态），4（显示与标记相关的消息），8（显示头部解析），16（记录写入网络的所有数据），32（调试强制功能），64（调试正则表达式过滤器），128（调试重定向），256（调试 GIF 去动画），512（通用日志格式），1024（记录 Privoxy 未通过的请求的目标及原因），2048（CGI 用户界面），4096（启动横幅和警告），8192（非致命错误），32768（记录从网络读取的所有数据），65536（记录应用的操作）。可以通过添加多个调试级别或使用多行调试语句来选择多个调试级别。 |
| `single-threaded` | 0 | `single-threaded 1` | 指定是否仅运行一个服务器线程。此选项仅用于调试目的，会显著降低性能。 |
| `hostname` | 未设置 | `hostname hostname.example.org` | 指定在 CGI 页面上显示的主机名。如果未设置，将使用操作系统提供的主机名。 |

## 4. ACCESS CONTROL AND SECURITY - 访问控制和安全参数

此配置文件部分控制 Privoxy 配置中与安全相关的方面。

| 参数名 | 默认值 | 示例 | 描述 |
|-|-|-|-|
| `listen-address` | `127.0.0.1:8118` | `listen-address 192.168.0.1:8118` | 指定 Privoxy 将监听客户端请求的地址和 TCP 端口。可以使用多次此语句，使 Privoxy 监听多个端口或 IP 地址。 |
| `toggle` | 1 | `toggle 0` | 指定 "toggle" 状态的初始状态。设置为 0 时，Privoxy 将以 "toggled off" 模式启动，即禁用广告拦截和内容过滤。 |
| `enable-remote-toggle` | 0 | `enable-remote-toggle 1` | 指定是否可以使用基于 Web 的切换功能。启用后，任何可以访问 Privoxy 的人都可以切换其状态。 |
| `enable-remote-http-toggle` | 0 | `enable-remote-http-toggle 1` | 指定 Privoxy 是否识别特殊的 HTTP 头以改变其行为。当前支持的特殊头是 "X-Filter: No"，用于禁用当前请求的过滤。 |
| `enable-edit-actions` | 0 | `enable-edit-actions 1` | 指定是否可以使用基于 Web 的动作文件编辑器。启用后，任何可以访问 Privoxy 的人都可以修改其配置。 |
| `enforce-blocks` | 0 | `enforce-blocks 1` | 指定用户是否可以忽略阻止并继续访问被阻止的页面。启用后，Privoxy 将隐藏 "go there anyway" 链接，并记录绕过尝试。 |
| `permit-access` | 未设置 | `permit-access 127.0.0.1` | 指定哪些客户端 IP 地址可以访问 Privoxy。可以使用多次此语句，允许多个地址或子网。 |
| `deny-access` | 未设置 | `deny-access 192.168.1.1` | 指定哪些客户端 IP 地址不能访问 Privoxy。可以使用多次此语句，拒绝多个地址或子网。 |
| `buffer-limit` | 4096 | `buffer-limit 8192` | 指定内容过滤的缓冲区最大大小（以 KB 为单位）。当文档缓冲区大小达到此限制时，缓冲区将被刷新到客户端且不再尝试过滤文档的其余部分。 |
| `enable-proxy-authentication-forwarding` | 0 | `enable-proxy-authentication-forwarding 1` | 指定是否允许通过 Privoxy 进行代理身份验证。启用后，Privoxy 将转发 Proxy-Authorization 和 Proxy-Authenticate 头。 |
| `trusted-cgi-referer` | 未设置 | `trusted-cgi-referer http://www.example.org/local-privoxy-control-page` | 指定可以访问敏感 CGI 页面的受信任网站或网页。 |
| `cors-allowed-origin` | 未设置 | `cors-allowed-origin http://www.example.org/` | 指定可以通过 JavaScript 访问 Privoxy CGI 页面的受信任网站。 |

## 5. FORWARDING - 转发参数

该功能允许通过多个代理链路路由 HTTP 请求。
转发可以用于将 Privoxy 与缓存代理链接起来，以加快浏览速度。如果运行 Privoxy 的机器没有直接的互联网访问权限，使用父代理也是必要的。
请注意，父代理可能会严重降低您的隐私级别。例如，父代理可能会将您的 IP 地址添加到请求头中，如果它是一个缓存代理，它可能会在重新验证请求中再次添加 "Etag" 头，即使您配置了 Privoxy 以删除它。它还可能忽略 Privoxy 的头部时间随机化，并使用原始值，这些值可能会被服务器用作 cookie 替代品，以在访问之间跟踪您的步骤。
此外，这里还指定了 SOCKS 代理。Privoxy 支持 SOCKS 4 和 SOCKS 4A 协议。

| 参数名 | 默认值 | 示例 | 描述 |
|-|-|-|-|
| `forward` | 未设置 | `forward / parent-proxy.example.org:8080` | 指定特定请求应路由到哪个父 HTTP 代理。`target_pattern` 是一个 URL 模式，指定此转发规则应适用于哪些请求（即 URL）。使用 `/` 表示“所有 URL”。`http_parent[:port]` 是父 HTTP 代理的 DNS 名称或 IP 地址，后跟其监听端口（默认：8000）。使用 `.` 表示“不转发”。 |
| `forward-socks4` | 未设置 | `forward-socks4 / socks-gw.example.com:1080 .` | 指定特定请求应通过哪个 SOCKS 4 代理（以及可选的父 HTTP 代理）进行路由。`target_pattern` 是一个 URL 模式，指定此转发规则应适用于哪些请求。`http_parent` 和 `socks_proxy` 是 IP 地址或有效的 DNS 名称，端口是 TCP 端口。 |
| `forward-socks4a` | 未设置 | `forward-socks4a / socks-gw.example.com:1080 www-cache.isp.example.net:8080` | 指定特定请求应通过哪个 SOCKS 4A 代理（以及可选的父 HTTP 代理）进行路由。与 SOCKS 4 不同，SOCKS 4A 协议中目标主机名的 DNS 解析发生在 SOCKS 服务器上。 |
| `forward-socks5` | 未设置 | `forward-socks5 / user:pass@socks-gw.example.com:1080 .` | 指定特定请求应通过哪个 SOCKS 5 代理（以及可选的父 HTTP 代理）进行路由。SOCKS 5 协议支持用户名/密码认证，DNS 解析在远程服务器上进行。 |
| `forward-socks5t` | 未设置 | `forward-socks5t / 127.0.0.1:9050 .` | 指定特定请求应通过哪个 SOCKS 5 代理（以及可选的父 HTTP 代理）进行路由，并使用 Tor 特定的 SOCKS 扩展。 |
| `forwarded-connect-retries` | 0 | `forwarded-connect-retries 1` | 指定如果转发的连接请求失败，Privoxy 重试的次数。主要用于 socks4a 连接，Privoxy 无法检测连接失败的原因。 |

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

HTTPS 检查允许过滤加密的请求和响应。只有在 Privoxy 使用 FEATURE_HTTPS_INSPECTION 构建时才支持此功能。如果您不确定您的版本是否支持此功能，请访问 http://config.privoxy.org/show-status 查看。

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
