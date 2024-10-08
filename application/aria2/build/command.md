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

### aria2c --help=#all

Usage: aria2c [OPTIONS] [URI | MAGNET | TORRENT_FILE | METALINK_FILE]...
Printing all options.

Options:
 -v, --version                Print the version number and exit.

                              Tags: #basic

 -h, --help[=TAG|KEYWORD]     Print usage and exit.
                              The help messages are classified with tags. A tag
                              starts with "#". For example, type "--help=#http"
                              to get the usage for the options tagged with
                              "#http". If non-tag word is given, print the usage
                              for the options whose name includes that word.

                              Possible Values: #basic, #advanced, #http, #https, #ftp, #metalink, #bittorrent, #cookie, #hook, #file, #rpc, #checksum, #experimental, #deprecated, #help, #all
                              Default: #basic
                              Tags: #basic, #help

 -t, --timeout=SEC            Set timeout in seconds.

                              Possible Values: 1-600
                              Default: 60
                              Tags: #http, #ftp

 --connect-timeout=SEC        Set the connect timeout in seconds to establish
                              connection to HTTP/FTP/proxy server. After the
                              connection is established, this option makes no
                              effect and --timeout option is used instead.

                              Possible Values: 1-600
                              Default: 60
                              Tags: #http, #ftp

 -m, --max-tries=N            Set number of tries. 0 means unlimited.

                              Possible Values: 0-*
                              Default: 5
                              Tags: #http, #ftp

 --auto-save-interval=SEC     Save a control file(*.aria2) every SEC seconds.
                              If 0 is given, a control file is not saved during
                              download. aria2 saves a control file when it stops
                              regardless of the value.

                              Possible Values: 0-600
                              Default: 60
                              Tags: #advanced

 -l, --log=LOG                The file name of the log file. If '-' is
                              specified, log is written to stdout.

                              Possible Values: /path/to/file, -
                              Tags: #basic

 -d, --dir=DIR                The directory to store the downloaded file.

                              Possible Values: /path/to/directory
                              Default: /
                              Tags: #basic, #file

 -o, --out=FILE               The file name of the downloaded file. It is
                              always relative to the directory given in -d
                              option. When the -Z option is used, this option
                              will be ignored.

                              Possible Values: /path/to/file
                              Tags: #basic, #http, #ftp, #file

 -s, --split=N                Download a file using N connections. If more
                              than N URIs are given, first N URIs are used and
                              remaining URLs are used for backup. If less than
                              N URIs are given, those URLs are used more than
                              once so that N connections total are made
                              simultaneously. The number of connections to the
                              same host is restricted by the 
                              --max-connection-per-server option. See also the
                              --min-split-size option.

                              Possible Values: 1-*
                              Default: 5
                              Tags: #basic, #http, #ftp

 -D, --daemon[=true|false]    Run as daemon. The current working directory will
                              be changed to "/" and standard input, standard
                              output and standard error will be redirected to
                              "/dev/null".

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced

 --referer=REFERER            Set an http referrrer (Referer). This affects
                              all http/https downloads. If "*" is given,
                              the download URI is also used as the referrer.
                              This may be useful when used together with
                              the -P option.

                              Tags: #http

 --lowest-speed-limit=SPEED   Close connection if download speed is lower than
                              or equal to this value(bytes per sec).
                              0 means aria2 does not have a lowest speed limit.
                              You can append K or M(1K = 1024, 1M = 1024K).
                              This option does not affect BitTorrent downloads.

                              Possible Values: 0-*
                              Default: 0
                              Tags: #http, #ftp

 --piece-length=LENGTH        Set a piece length for HTTP/FTP downloads. This
                              is the boundary when aria2 splits a file. All
                              splits occur at multiple of this length. This
                              option will be ignored in BitTorrent downloads.
                              It will be also ignored if Metalink file
                              contains piece hashes.

                              Possible Values: 1048576-1073741824
                              Default: 1M
                              Tags: #advanced, #http, #ftp

 --max-overall-download-limit=SPEED Set max overall download speed in bytes/sec.
                              0 means unrestricted.
                              You can append K or M(1K = 1024, 1M = 1024K).
                              To limit the download speed per download, use
                              --max-download-limit option.

                              Possible Values: 0-*
                              Default: 0
                              Tags: #http, #ftp, #bittorrent

 --max-download-limit=SPEED   Set max download speed per each download in
                              bytes/sec. 0 means unrestricted.
                              You can append K or M(1K = 1024, 1M = 1024K).
                              To limit the overall download speed, use
                              --max-overall-download-limit option.

                              Possible Values: 0-*
                              Default: 0
                              Tags: #http, #ftp, #bittorrent

 --file-allocation=METHOD     Specify file allocation method.
                              'none' doesn't pre-allocate file space. 'prealloc'
                              pre-allocates file space before download begins.
                              This may take some time depending on the size of
                              the file.
                              If you are using newer file systems such as ext4
                              (with extents support), btrfs, xfs or NTFS
                              (MinGW build only), 'falloc' is your best
                              choice. It allocates large(few GiB) files
                              almost instantly. Don't use 'falloc' with legacy
                              file systems such as ext3 and FAT32 because it
                              takes almost the same time as 'prealloc' and it
                              blocks aria2 entirely until allocation finishes.
                              'falloc' may not be available if your system
                              doesn't have posix_fallocate() function.
                              'trunc' uses ftruncate() system call or
                              platform-specific counterpart to truncate a file
                              to a specified length.

                              Possible Values: none, prealloc, trunc, falloc
                              Default: prealloc
                              Tags: #basic, #file

 --no-file-allocation-limit=SIZE No file allocation is made for files whose
                              size is smaller than SIZE.
                              You can append K or M(1K = 1024, 1M = 1024K).

                              Possible Values: 0-*
                              Default: 5M
                              Tags: #advanced, #file

 --allow-overwrite[=true|false] Restart download from scratch if the
                              corresponding control file doesn't exist.  See
                              also --auto-file-renaming option.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced, #file

 --realtime-chunk-checksum[=true|false]  Validate chunk of data by calculating
                              checksum while downloading a file if chunk
                              checksums are provided.

                              Possible Values: true, false
                              Default: true
                              Tags: #metalink, #checksum

 -V, --check-integrity[=true|false] Check file integrity by validating piece
                              hashes or a hash of entire file. This option has
                              effect only in BitTorrent, Metalink downloads
                              with checksums or HTTP(S)/FTP downloads with
                              --checksum option. If piece hashes are provided,
                              this option can detect damaged portions of a file
                              and re-download them. If a hash of entire file is
                              provided, hash check is only done when file has
                              been already download. This is determined by file
                              length. If hash check fails, file is
                              re-downloaded from scratch. If both piece hashes
                              and a hash of entire file are provided, only
                              piece hashes are used.

                              Possible Values: true, false
                              Default: false
                              Tags: #basic, #metalink, #bittorrent, #file, #checksum

 --netrc-path=FILE            Specify the path to the netrc file.

                              Possible Values: /path/to/file
                              Default: /root/.netrc
                              Tags: 

 -c, --continue[=true|false]  Continue downloading a partially downloaded
                              file. Use this option to resume a download
                              started by a web browser or another program
                              which downloads files sequentially from the
                              beginning. Currently this option is only
                              applicable to http(s)/ftp downloads.

                              Possible Values: true, false
                              Default: false
                              Tags: #basic, #http, #ftp

 -n, --no-netrc[=true|false]  Disables netrc support.

                              Possible Values: true, false
                              Default: false
                              Tags: #http, #ftp

 -i, --input-file=FILE        Downloads URIs found in FILE. You can specify
                              multiple URIs for a single entity: separate
                              URIs on a single line using the TAB character.
                              Reads input from stdin when '-' is specified.
                              Additionally, options can be specified after each
                              line of URI. This optional line must start with
                              one or more white spaces and have one option per
                              single line. See INPUT FILE section of man page
                              for details. See also --deferred-input option.

                              Possible Values: /path/to/file, -
                              Tags: #basic

 --deferred-input[=true|false] If true is given, aria2 does not read all URIs
                              and options from file specified by -i option at
                              startup, but it reads one by one when it needs
                              later. This may reduce memory usage if input
                              file contains a lot of URIs to download.
                              If false is given, aria2 reads all URIs and
                              options at startup.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced

 -j, --max-concurrent-downloads=N Set maximum number of parallel downloads for
                              every static (HTTP/FTP) URL, torrent and metalink.
                              See also --split and --optimize-concurrent-downloads options.

                              Possible Values: 1-*
                              Default: 5
                              Tags: #basic

 --optimize-concurrent-downloads[=true|false|A:B] Optimizes the number of
                              concurrent downloads according to the bandwidth
                              available. aria2 uses the download speed observed
                              in the previous downloads to adapt the number of
                              downloads launched in parallel according to the
                              rule N = A + B Log10(speed in Mbps). The
                              coefficients A and B can be customized in the
                              option arguments with A and B separated by a
                              colon. The default values (A=5,B=25) lead to
                              using typically 5 parallel downloads on 1Mbps
                              networks and above 50 on 100Mbps networks. The
                              number of parallel downloads remains constrained
                              under the maximum defined by the
                              max-concurrent-downloads parameter.

                              Possible Values: true, false, A:B
                              Default: false
                              Tags: #advanced

 -Z, --force-sequential[=true|false] Fetch URIs in the command-line sequentially
                              and download each URI in a separate session, like
                              the usual command-line download utilities.

                              Possible Values: true, false
                              Default: false
                              Tags: #basic

 --auto-file-renaming[=true|false] Rename file name if the same file already
                              exists. This option works only in http(s)/ftp
                              download.
                              The new file name has a dot and a number(1..9999)
                              appended after the name, but before the file
                              extension, if any.

                              Possible Values: true, false
                              Default: true
                              Tags: #advanced, #file

 -P, --parameterized-uri[=true|false] Enable parameterized URI support.
                              You can specify set of parts:
                              http://{sv1,sv2,sv3}/foo.iso
                              Also you can specify numeric sequences with step
                              counter:
                              http://host/image[000-100:2].img
                              A step counter can be omitted.
                              If all URIs do not point to the same file, such
                              as the second example above, -Z option is
                              required.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced

 --allow-piece-length-change[=true|false] If false is given, aria2 aborts
                              download when a piece length is different from
                              one in a control file. If true is given, you can
                              proceed but some download progress will be lost.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced

 --no-conf[=true|false]       Disable loading aria2.conf file.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced

 --conf-path=PATH             Change the configuration file path to PATH.

                              Possible Values: /path/to/file
                              Default: /root/.config/aria2/aria2.conf
                              Tags: #advanced

 --stop=SEC                   Stop application after SEC seconds has passed.
                              If 0 is given, this feature is disabled.

                              Possible Values: 0-2147483647
                              Default: 0
                              Tags: #advanced

 -q, --quiet[=true|false]     Make aria2 quiet(no console output).

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced

 --async-dns[=true|false]     Enable asynchronous DNS.

                              Possible Values: true, false
                              Default: true
                              Tags: #advanced

 --summary-interval=SEC       Set interval to output download progress summary.
                              Setting 0 suppresses the output.

                              Possible Values: 0-2147483647
                              Default: 60
                              Tags: #advanced

 --log-level=LEVEL            Set log level to output to file specified using
                             --log option.

                              Possible Values: debug, info, notice, warn, error
                              Default: debug
                              Tags: #advanced

 --console-log-level=LEVEL    Set log level to output to console.

                              Possible Values: debug, info, notice, warn, error
                              Default: notice
                              Tags: #advanced

 --uri-selector=SELECTOR      Specify URI selection algorithm.
                              If 'inorder' is given, URI is tried in the order
                              appeared in the URI list.
                              If 'feedback' is given, aria2 uses download speed
                              observed in the previous downloads and choose
                              fastest server in the URI list. This also
                              effectively skips dead mirrors. The observed
                              download speed is a part of performance profile
                              of servers mentioned in --server-stat-of and
                              --server-stat-if options.
                              If 'adaptive' is given, selects one of the best
                              mirrors for the first and reserved connections.
                              For supplementary ones, it returns mirrors which
                              has not been tested yet, and if each of them has
                              already been tested, returns mirrors which has to
                              be tested again. Otherwise, it doesn't select
                              anymore mirrors. Like 'feedback', it uses a
                              performance profile of servers.

                              Possible Values: inorder, feedback, adaptive
                              Default: feedback
                              Tags: #http, #ftp

 --server-stat-timeout=SEC    Specifies timeout in seconds to invalidate
                              performance profile of the servers since the last
                              contact to them.

                              Possible Values: 0-2147483647
                              Default: 86400
                              Tags: #http, #ftp

 --server-stat-if=FILE        Specify the filename to load performance profile
                              of the servers. The loaded data will be used in
                              some URI selector such as 'feedback'.
                              See also --uri-selector option

                              Possible Values: /path/to/file
                              Tags: #http, #ftp

 --server-stat-of=FILE        Specify the filename to which performance profile
                              of the servers is saved. You can load saved data
                              using --server-stat-if option.

                              Possible Values: /path/to/file
                              Tags: #http, #ftp

 -R, --remote-time[=true|false] Retrieve timestamp of the remote file from the
                              remote HTTP/FTP server and if it is available,
                              apply it to the local file.

                              Possible Values: true, false
                              Default: false
                              Tags: #http, #ftp

 --max-file-not-found=NUM     If aria2 receives `file not found' status from the
                              remote HTTP/FTP servers NUM times without getting
                              a single byte, then force the download to fail.
                              Specify 0 to disable this option.
                              This options is effective only when using
                              HTTP/FTP servers. The number of retry attempt is
                              counted toward --max-tries, so it should be
                              configured too.

                              Possible Values: 0-*
                              Default: 0
                              Tags: #http, #ftp

 --event-poll=POLL            Specify the method for polling events.

                              Possible Values: epoll, poll, select
                              Default: epoll
                              Tags: #advanced

 --enable-rpc[=true|false]    Enable JSON-RPC/XML-RPC server.
                              It is strongly recommended to set secret
                              authorization token using --rpc-secret option.
                              See also --rpc-listen-port option.

                              Possible Values: true, false
                              Default: false
                              Tags: #rpc

 --rpc-listen-port=PORT       Specify a port number for JSON-RPC/XML-RPC server
                              to listen to.

                              Possible Values: 1024-65535
                              Default: 6800
                              Tags: #rpc

 --rpc-user=USER              Set JSON-RPC/XML-RPC user. This option will be
                              deprecated in the future release. Migrate to
                              --rpc-secret option as soon as possible.

                              Tags: #rpc, #deprecated

 --rpc-passwd=PASSWD          Set JSON-RPC/XML-RPC password. This option will
                              be deprecated in the future release. Migrate to
                              --rpc-secret option as soon as possible.

                              Tags: #rpc, #deprecated

 --rpc-max-request-size=SIZE  Set max size of JSON-RPC/XML-RPC request. If aria2
                              detects the request is more than SIZE bytes, it
                              drops connection.

                              Possible Values: 0-*
                              Default: 2M
                              Tags: #rpc

 --rpc-listen-all[=true|false] Listen incoming JSON-RPC/XML-RPC requests on all
                              network interfaces. If false is given, listen only
                              on local loopback interface.

                              Possible Values: true, false
                              Default: false
                              Tags: #rpc

 --rpc-allow-origin-all[=true|false] Add Access-Control-Allow-Origin header
                              field with value '*' to the RPC response.

                              Possible Values: true, false
                              Default: false
                              Tags: #rpc

 --rpc-certificate=FILE       Use the certificate in FILE for RPC server.
                              The certificate must be in PEM format.
                              Use --rpc-private-key option to specify the
                              private key. Use --rpc-secure option to enable
                              encryption.

                              Possible Values: /path/to/file
                              Tags: #rpc

 --rpc-private-key=FILE       Use the private key in FILE for RPC server.
                              The private key must be decrypted and in PEM
                              format. Use --rpc-secure option to enable
                              encryption. See also --rpc-certificate option.

                              Possible Values: /path/to/file
                              Tags: #rpc

 --rpc-secure[=true|false]    RPC transport will be encrypted by SSL/TLS.
                              The RPC clients must use https scheme to access
                              the server. For WebSocket client, use wss
                              scheme. Use --rpc-certificate and
                              --rpc-private-key options to specify the
                              server certificate and private key.

                              Possible Values: true, false
                              Default: false
                              Tags: #rpc

 --rpc-save-upload-metadata[=true|false] Save the uploaded torrent or
                              metalink metadata in the directory specified
                              by --dir option. The filename consists of
                              SHA-1 hash hex string of metadata plus
                              extension. For torrent, the extension is
                              '.torrent'. For metalink, it is '.meta4'.
                              If false is given to this option, the
                              downloads added by aria2.addTorrent or
                              aria2.addMetalink will not be saved by
                              --save-session option.

                              Possible Values: true, false
                              Default: true
                              Tags: #rpc

 --dry-run[=true|false]       If true is given, aria2 just checks whether the
                              remote file is available and doesn't download
                              data. This option has effect on HTTP/FTP download.
                              BitTorrent downloads are canceled if true is
                              specified.

                              Possible Values: true, false
                              Default: false
                              Tags: #http, #ftp

 --reuse-uri[=true|false]     Reuse already used URIs if no unused URIs are
                              left.

                              Possible Values: true, false
                              Default: true
                              Tags: #http, #ftp

 --on-download-start=COMMAND  Set the command to be executed after download
                              got started. aria2 passes 3 arguments to COMMAND:
                              GID, the number of files and file path. See Event
                              Hook in man page for more details.

                              Possible Values: /path/to/command
                              Tags: #advanced, #hook

 --on-download-pause=COMMAND  Set the command to be executed after download
                              was paused.
                              See --on-download-start option for the
                              requirement of COMMAND.

                              Possible Values: /path/to/command
                              Tags: #advanced, #hook

 --on-download-stop=COMMAND   Set the command to be executed after download
                              stopped. You can override the command to be
                              executed for particular download result using
                              --on-download-complete and --on-download-error. If
                              they are specified, command specified in this
                              option is not executed.
                              See --on-download-start option for the
                              requirement of COMMAND.

                              Possible Values: /path/to/command
                              Tags: #advanced, #hook

 --on-download-complete=COMMAND Set the command to be executed after download
                              completed.
                              See --on-download-start option for the
                              requirement of COMMAND.
                              See also --on-download-stop option.

                              Possible Values: /path/to/command
                              Tags: #advanced, #hook

 --on-download-error=COMMAND  Set the command to be executed after download
                              aborted due to error.
                              See --on-download-start option for the
                              requirement of COMMAND.
                              See also --on-download-stop option.

                              Possible Values: /path/to/command
                              Tags: #advanced, #hook

 --interface=INTERFACE        Bind sockets to given interface. You can specify
                              interface name, IP address and hostname.

                              Possible Values: interface, IP address, hostname
                              Tags: #advanced

 --multiple-interface=INTERFACES Comma separated list of interfaces to bind
                              sockets to. Requests will be split among the
                              interfaces to achieve link aggregation. You can
                              specify interface name, IP address and hostname.
                              If --interface is used, this option will be
                              ignored.

                              Possible Values: interface, IP address, hostname
                              Tags: #advanced

 --disable-ipv6[=true|false]  Disable IPv6.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced

 --human-readable[=true|false] Print sizes and speed in human readable format
                              (e.g., 1.2Ki, 3.4Mi) in the console readout.

                              Possible Values: true, false
                              Default: true
                              Tags: #advanced

 --remove-control-file[=true|false] Remove control file before download. Using
                              with --allow-overwrite=true, download always
                              starts from scratch. This will be useful for
                              users behind proxy server which disables resume.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced

 --always-resume[=true|false] Always resume download. If true is given, aria2
                              always tries to resume download and if resume is
                              not possible, aborts download. If false is given,
                              when all given URIs do not support resume or
                              aria2 encounters N URIs which does not support
                              resume (N is the value specified using
                              --max-resume-failure-tries option), aria2
                              downloads file from scratch.
                              See --max-resume-failure-tries option.

                              Possible Values: true, false
                              Default: true
                              Tags: #advanced, #http, #ftp

 --max-resume-failure-tries=N When used with --always-resume=false, aria2
                              downloads file from scratch when aria2 detects N
                              number of URIs that does not support resume. If N
                              is 0, aria2 downloads file from scratch when all
                              given URIs do not support resume.
                              See --always-resume option.

                              Possible Values: 0-*
                              Default: 0
                              Tags: #advanced, #http, #ftp

 --save-session=FILE          Save error/unfinished downloads to FILE on exit.
                              You can pass this output file to aria2c with -i
                              option on restart. Please note that downloads
                              added by aria2.addTorrent and aria2.addMetalink
                              RPC method and whose metadata could not be saved
                              as a file will not be saved. Downloads removed
                              using aria2.remove and aria2.forceRemove will not
                              be saved.

                              Possible Values: /path/to/file
                              Tags: #advanced

 -x, --max-connection-per-server=NUM The maximum number of connections to one
                              server for each download.

                              Possible Values: 1-16
                              Default: 1
                              Tags: #basic, #http, #ftp

 -k, --min-split-size=SIZE    aria2 does not split less than 2*SIZE byte range.
                              For example, let's consider downloading 20MiB
                              file. If SIZE is 10M, aria2 can split file into 2
                              range [0-10MiB) and [10MiB-20MiB) and download it
                              using 2 sources(if --split >= 2, of course).
                              If SIZE is 15M, since 2*15M > 20MiB, aria2 does
                              not split file and download it using 1 source.
                              You can append K or M(1K = 1024, 1M = 1024K).

                              Possible Values: 1048576-1073741824
                              Default: 20M
                              Tags: #basic, #http, #ftp

 --conditional-get[=true|false] Download file only when the local file is older
                              than remote file. Currently, this function has
                              many limitations. See man page for details.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced, #http

 --enable-async-dns6[=true|false] Enable IPv6 name resolution in asynchronous
                              DNS resolver. This option will be ignored when
                              --async-dns=false.

                              Possible Values: true, false
                              Tags: #advanced, #deprecated

 --max-download-result=NUM    Set maximum number of download result kept in
                              memory. The download results are completed/error/
                              removed downloads. The download results are stored
                              in FIFO queue and it can store at most NUM
                              download results. When queue is full and new
                              download result is created, oldest download result
                              is removed from the front of the queue and new one
                              is pushed to the back. Setting big number in this
                              option may result high memory consumption after
                              thousands of downloads. Specifying 0 means no
                              download result is kept. Note that unfinished
                              downloads are kept in memory regardless of this
                              option value. See
                              --keep-unfinished-download-result option.

                              Possible Values: 0-*
                              Default: 1000
                              Tags: #advanced

 --retry-wait=SEC             Set the seconds to wait between retries. 
                              With SEC > 0, aria2 will retry download when the
                              HTTP server returns 503 response.

                              Possible Values: 0-600
                              Default: 0
                              Tags: #http, #ftp

 --async-dns-server=IPADDRESS[,...] Comma separated list of DNS server address
                              used in asynchronous DNS resolver. Usually
                              asynchronous DNS resolver reads DNS server
                              addresses from /etc/resolv.conf. When this option
                              is used, it uses DNS servers specified in this
                              option instead of ones in /etc/resolv.conf. You
                              can specify both IPv4 and IPv6 address. This
                              option is useful when the system does not have
                              /etc/resolv.conf and user does not have the
                              permission to create it.

                              Tags: #advanced

 --show-console-readout[=true|false] Show console readout.

                              Possible Values: true, false
                              Default: true
                              Tags: #advanced

 --stream-piece-selector=SELECTOR Specify piece selection algorithm
                              used in HTTP/FTP download. Piece means fixed
                              length segment which is downloaded in parallel
                              in segmented download. If 'default' is given,
                              aria2 selects piece so that it reduces the
                              number of establishing connection. This is
                              reasonable default behaviour because
                              establishing connection is an expensive
                              operation.
                              If 'inorder' is given, aria2 selects piece which
                              has minimum index. Index=0 means first of the
                              file. This will be useful to view movie while
                              downloading it. --enable-http-pipelining option
                              may be useful to reduce reconnection overhead.
                              Please note that aria2 honors
                              --min-split-size option, so it will be necessary
                              to specify a reasonable value to
                              --min-split-size option.
                              If 'random' is given, aria2 selects piece
                              randomly. Like 'inorder', --min-split-size
                              option is honored.
                              If 'geom' is given, at the beginning aria2
                              selects piece which has minimum index like
                              'inorder', but it exponentially increasingly
                              keeps space from previously selected piece. This
                              will reduce the number of establishing connection
                              and at the same time it will download the
                              beginning part of the file first. This will be
                              useful to view movie while downloading it.

                              Possible Values: default, inorder, random, geom
                              Default: default
                              Tags: #http, #ftp

 --truncate-console-readout[=true|false] Truncate console readout to fit in
                              a single line.

                              Possible Values: true, false
                              Default: true
                              Tags: #advanced

 --pause[=true|false]         Pause download after added. This option is
                              effective only when --enable-rpc=true is given.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced, #rpc

 --download-result=OPT        This option changes the way "Download Results"
                              is formatted. If OPT is 'default', print GID,
                              status, average download speed and path/URI. If
                              multiple files are involved, path/URI of first
                              requested file is printed and remaining ones are
                              omitted.
                              If OPT is 'full', print GID, status, average
                              download speed, percentage of progress and
                              path/URI. The percentage of progress and
                              path/URI are printed for each requested file in
                              each row.
                              If OPT is 'hide', "Download Results" is hidden.

                              Possible Values: default, full, hide
                              Default: default
                              Tags: #advanced

 --hash-check-only[=true|false] If true is given, after hash check using
                              --check-integrity option, abort download whether
                              or not download is complete.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced, #metalink, #bittorrent, #file, #checksum

 --checksum=TYPE=DIGEST       Set checksum. TYPE is hash type. The supported
                              hash type is listed in "Hash Algorithms" in
                              "aria2c -v". DIGEST is hex digest.
                              For example, setting sha-1 digest looks like
                              this:
                              sha-1=0192ba11326fe2298c8cb4de616f4d4140213838
                              This option applies only to HTTP(S)/FTP
                              downloads.

                              Possible Values: HASH_TYPE=HEX_DIGEST
                              Tags: #http, #ftp, #checksum

 --stop-with-process=PID      Stop application when process PID is not running.
                              This is useful if aria2 process is forked from a
                              parent process. The parent process can fork aria2
                              with its own pid and when parent process exits
                              for some reason, aria2 can detect it and shutdown
                              itself.

                              Possible Values: 0-*
                              Tags: #advanced

 --enable-mmap[=true|false]   Map files into memory.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced, #experimental

 --force-save[=true|false]    Save download with --save-session option even
                              if the download is completed or removed. This
                              option also saves control file in that
                              situations. This may be useful to save
                              BitTorrent seeding which is recognized as
                              completed state.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced

 --save-not-found[=true|false] Save download with --save-session option even
                              if the file was not found on the server. This
                              option also saves control file in that
                              situations.

                              Possible Values: true, false
                              Default: true
                              Tags: #advanced

 --disk-cache=SIZE            Enable disk cache. If SIZE is 0, the disk cache
                              is disabled. This feature caches the downloaded
                              data in memory, which grows to at most SIZE
                              bytes. The cache storage is created for aria2
                              instance and shared by all downloads. The one
                              advantage of the disk cache is reduce the disk
                              I/O because the data are written in larger unit
                              and it is reordered by the offset of the file.
                              If hash checking is involved and the data are
                              cached in memory, we don't need to read them
                              from the disk.
                              SIZE can include K or M(1K = 1024, 1M = 1024K).

                              Possible Values: 0-*
                              Default: 16M
                              Tags: #advanced

 --gid=GID                    Set GID manually. aria2 identifies each
                              download by the ID called GID. The GID must be
                              hex string of 16 characters, thus [0-9a-fA-F]
                              are allowed and leading zeros must not be
                              stripped. The GID all 0 is reserved and must
                              not be used. The GID must be unique, otherwise
                              error is reported and the download is not added.
                              This option is useful when restoring the
                              sessions saved using --save-session option. If
                              this option is not used, new GID is generated
                              by aria2.

                              Tags: #advanced

 --save-session-interval=SEC  Save error/unfinished downloads to a file
                              specified by --save-session option every SEC
                              seconds. If 0 is given, file will be saved only
                              when aria2 exits.

                              Possible Values: 0-*
                              Default: 0
                              Tags: #advanced

 --enable-color[=true|false]  Enable color output for a terminal.

                              Possible Values: true, false
                              Default: true
                              Tags: #advanced

 --rpc-secret=TOKEN           Set RPC secret authorization token.

                              Tags: #rpc

 --dscp=DSCP                  Set DSCP value in outgoing IP packets of
                              BitTorrent traffic for QoS. This parameter sets
                              only DSCP bits in TOS field of IP packets,
                              not the whole field. If you take values
                              from /usr/include/netinet/ip.h divide them by 4
                              (otherwise values would be incorrect, e.g. your
                              CS1 class would turn into CS4). If you take
                              commonly used values from RFC, network vendors'
                              documentation, Wikipedia or any other source,
                              use them as they are.

                              Possible Values: 0-*
                              Default: 0
                              Tags: #advanced

 --pause-metadata[=true|false]
                              Pause downloads created as a result of metadata
                              download. There are 3 types of metadata
                              downloads in aria2: (1) downloading .torrent
                              file. (2) downloading torrent metadata using
                              magnet link. (3) downloading metalink file.
                              These metadata downloads will generate downloads
                              using their metadata. This option pauses these
                              subsequent downloads. This option is effective
                              only when --enable-rpc=true is given.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced, #rpc

 --rlimit-nofile=NUM          Set the soft limit of open file descriptors.
                              This open will only have effect when:
                                a) The system supports it (posix)
                                b) The limit does not exceed the hard limit.
                                c) The specified limit is larger than the
                                   current soft limit.
                              This is equivalent to setting nofile via ulimit,
                              except that it will never decrease the limit.

                              Possible Values: 1-*
                              Default: 1024
                              Tags: #advanced

 --min-tls-version=VERSION    Specify minimum SSL/TLS version to enable.

                              Possible Values: TLSv1.1, TLSv1.2, TLSv1.3
                              Default: TLSv1.2
                              Tags: #advanced

 --socket-recv-buffer-size=SIZE
                              Set the maximum socket receive buffer in bytes.
                              Specifying 0 will disable this option. This value
                              will be set to socket file descriptor using
                              SO_RCVBUF socket option with setsockopt() call.

                              Possible Values: 0-16777216
                              Default: 0
                              Tags: #advanced

 --max-mmap-limit=SIZE        Set the maximum file size to enable mmap (see
                              --enable-mmap option). The file size is
                              determined by the sum of all files contained in
                              one download. For example, if a download
                              contains 5 files, then file size is the total
                              size of those files. If file size is strictly
                              greater than the size specified in this option,
                              mmap will be disabled.

                              Possible Values: 0-*
                              Default: 9223372036854775807
                              Tags: #advanced

 --stderr[=true|false]        Redirect all console output that would be
                              otherwise printed in stdout to stderr.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced

 --keep-unfinished-download-result[=true|false]
                              Keep unfinished download results even if doing
                              so exceeds --max-download-result. This is useful
                              if all unfinished downloads must be saved in
                              session file (see --save-session option). Please
                              keep in mind that there is no upper bound to the
                              number of unfinished download result to keep. If
                              that is undesirable, turn this option off.

                              Possible Values: true, false
                              Default: true
                              Tags: #advanced

 --ftp-user=USER              Set FTP user. This affects all URLs.

                              Tags: #basic, #ftp

 --ftp-passwd=PASSWD          Set FTP password. This affects all URLs.

                              Tags: #basic, #ftp

 --ftp-type=TYPE              Set FTP transfer type.

                              Possible Values: binary, ascii
                              Default: binary
                              Tags: #ftp

 -p, --ftp-pasv[=true|false]  Use the passive mode in FTP. If false is given,
                              the active mode will be used.

                              Possible Values: true, false
                              Default: true
                              Tags: #ftp

 --ftp-reuse-connection[=true|false] Reuse connection in FTP.

                              Possible Values: true, false
                              Default: true
                              Tags: #ftp

 --ssh-host-key-md=TYPE=DIGEST
                              Set checksum for SSH host public key. TYPE is
                              hash type. The supported hash type is sha-1 or
                              md5. DIGEST is hex digest. For example:
                              sha-1=b030503d4de4539dc7885e6f0f5e256704edf4c3
                              This option can be used to validate server's
                              public key when SFTP is used. If this option is
                              not set, which is default, no validation takes
                              place.

                              Possible Values: HASH_TYPE=HEX_DIGEST
                              Tags: #ftp

 --http-user=USER             Set HTTP user. This affects all URLs.

                              Tags: #basic, #http

 --http-passwd=PASSWD         Set HTTP password. This affects all URLs.

                              Tags: #basic, #http

 -U, --user-agent=USER_AGENT  Set user agent for http(s) downloads.

                              Default: aria2/1.37.0
                              Tags: #http

 --load-cookies=FILE          Load Cookies from FILE using the Firefox3 format
                              and Mozilla/Firefox(1.x/2.x)/Netscape format.

                              Possible Values: /path/to/file
                              Tags: #basic, #http, #cookie

 --save-cookies=FILE          Save Cookies to FILE in Mozilla/Firefox(1.x/2.x)/
                              Netscape format. If FILE already exists, it is
                              overwritten. Session Cookies are also saved and
                              their expiry values are treated as 0.

                              Possible Values: /path/to/file
                              Tags: #http, #cookie

 --enable-http-keep-alive[=true|false] Enable HTTP/1.1 persistent connection.

                              Possible Values: true, false
                              Default: true
                              Tags: #http

 --enable-http-pipelining[=true|false] Enable HTTP/1.1 pipelining.

                              Possible Values: true, false
                              Default: false
                              Tags: #http

 --header=HEADER              Append HEADER to HTTP request header. You can use
                              this option repeatedly to specify more than one
                              header:
                              aria2c --header="X-A: b78" --header="X-B: 9J1"
                              http://host/file

                              Tags: #http

 --certificate=FILE           Use the client certificate in FILE.
                              The certificate must be in PEM format.
                              You may use --private-key option to specify the
                              private key.

                              Possible Values: /path/to/file
                              Tags: #http, #https

 --private-key=FILE           Use the private key in FILE.
                              The private key must be decrypted and in PEM
                              format. See also --certificate option.

                              Possible Values: /path/to/file
                              Tags: #http, #https

 --ca-certificate=FILE        Use the certificate authorities in FILE to verify
                              the peers. The certificate file must be in PEM
                              format and can contain multiple CA certificates.
                              Use --check-certificate option to enable
                              verification.

                              Possible Values: /path/to/file
                              Default: /etc/ssl/certs/ca-certificates.crt
                              Tags: #http, #https

 --check-certificate[=true|false] Verify the peer using certificates specified
                              in --ca-certificate option.

                              Possible Values: true, false
                              Default: true
                              Tags: #http, #https

 --use-head[=true|false]      Use HEAD method for the first request to the HTTP
                              server.

                              Possible Values: true, false
                              Default: false
                              Tags: #http

 --http-auth-challenge[=true|false] Send HTTP authorization header only when it
                              is requested by the server. If false is set, then
                              authorization header is always sent to the server.
                              There is an exception: if username and password
                              are embedded in URI, authorization header is
                              always sent to the server regardless of this
                              option.

                              Possible Values: true, false
                              Default: false
                              Tags: #http

 --http-no-cache[=true|false] Send Cache-Control: no-cache and Pragma: no-cache
                              header to avoid cached content.  If false is
                              given, these headers are not sent and you can add
                              Cache-Control header with a directive you like
                              using --header option.

                              Possible Values: true, false
                              Default: false
                              Tags: #http

 --http-accept-gzip[=true|false] Send 'Accept-Encoding: deflate, gzip' request
                              header and inflate response if remote server
                              responds with 'Content-Encoding: gzip' or
                              'Content-Encoding: deflate'.

                              Possible Values: true, false
                              Default: false
                              Tags: #http

 --content-disposition-default-utf8[=true|false] Handle quoted string in
                              Content-Disposition header as UTF-8 instead of
                              ISO-8859-1, for example, the filename parameter,
                              but not the extended version filename*.

                              Possible Values: true, false
                              Default: false
                              Tags: #advanced, #http

 --no-want-digest-header[=true|false] Whether to disable Want-Digest header 
                              when doing requests.

                              Possible Values: true, false
                              Default: false
                              Tags: #http

 --http-proxy=PROXY           Use a proxy server for HTTP. To override a
                              previously defined proxy, use "".
                              See also the --all-proxy option.
                              This affects all http downloads.

                              Possible Values: [http://][USER:PASSWORD@]HOST[:PORT]
                              Tags: #http

 --https-proxy=PROXY          Use a proxy server for HTTPS. To override a 
                              previously defined proxy, use "".
                              See also the --all-proxy option.
                              This affects all https downloads.

                              Possible Values: [http://][USER:PASSWORD@]HOST[:PORT]
                              Tags: #http, #https

 --ftp-proxy=PROXY            Use a proxy server for FTP. To override a 
                              previously defined proxy, use "".
                              See also the --all-proxy option.
                              This affects all ftp downloads.

                              Possible Values: [http://][USER:PASSWORD@]HOST[:PORT]
                              Tags: #ftp

 --all-proxy=PROXY            Use a proxy server for all protocols. To override
                              a previously defined proxy, use "".
                              You also can override this setting and specify a
                              proxy server for a particular protocol using the
                              --http-proxy, --https-proxy and --ftp-proxy
                              options.
                              This affects all downloads.

                              Possible Values: [http://][USER:PASSWORD@]HOST[:PORT]
                              Tags: #http, #https, #ftp

 --no-proxy=DOMAINS           Specify comma separated hostnames, domains or
                              network address with or without CIDR block where
                              proxy should not be used.

                              Possible Values: HOSTNAME,DOMAIN,NETWORK/CIDR
                              Tags: #http, #https, #ftp

 --proxy-method=METHOD        Set the method to use in proxy request.

                              Possible Values: get, tunnel
                              Default: get
                              Tags: #http, #ftp

 --http-proxy-user=USER       Set user for --http-proxy.

                              Tags: #http

 --http-proxy-passwd=PASSWD   Set password for --http-proxy.

                              Tags: #http

 --https-proxy-user=USER      Set user for --https-proxy.

                              Tags: #http, #https

 --https-proxy-passwd=PASSWD  Set password for --https-proxy.

                              Tags: #http, #https

 --ftp-proxy-user=USER        Set user for --ftp-proxy.

                              Tags: #ftp

 --ftp-proxy-passwd=PASSWD    Set password for --ftp-proxy.

                              Tags: #ftp

 --all-proxy-user=USER        Set user for --all-proxy.

                              Tags: #http, #https, #ftp

 --all-proxy-passwd=PASSWD    Set password for --all-proxy.

                              Tags: #http, #https, #ftp

 -S, --show-files[=true|false] Print file listing of .torrent, .meta4 and
                              .metalink file and exit. More detailed
                              information will be listed in case of torrent
                              file.

                              Possible Values: true, false
                              Default: false
                              Tags: #basic, #metalink, #bittorrent

 --max-overall-upload-limit=SPEED Set max overall upload speed in bytes/sec.
                              0 means unrestricted.
                              You can append K or M(1K = 1024, 1M = 1024K).
                              To limit the upload speed per torrent, use
                              --max-upload-limit option.

                              Possible Values: 0-*
                              Default: 0
                              Tags: #basic, #bittorrent

 -u, --max-upload-limit=SPEED Set max upload speed per each torrent in
                              bytes/sec. 0 means unrestricted.
                              You can append K or M(1K = 1024, 1M = 1024K).
                              To limit the overall upload speed, use
                              --max-overall-upload-limit option.

                              Possible Values: 0-*
                              Default: 0
                              Tags: #basic, #bittorrent

 -T, --torrent-file=TORRENT_FILE  The path to the .torrent file.

                              Possible Values: /path/to/file
                              Tags: #basic, #bittorrent

 --listen-port=PORT...        Set TCP port number for BitTorrent downloads.
                              Multiple ports can be specified by using ',',
                              for example: "6881,6885". You can also use '-'
                              to specify a range: "6881-6999". ',' and '-' can
                              be used together.

                              Possible Values: 1024-65535
                              Default: 6881-6999
                              Tags: #basic, #bittorrent

 --follow-torrent=true|false|mem If true or mem is specified, when a file
                              whose suffix is .torrent or content type is
                              application/x-bittorrent is downloaded, aria2
                              parses it as a torrent file and downloads files
                              mentioned in it.
                              If mem is specified, a torrent file is not
                              written to the disk, but is just kept in memory.
                              If false is specified, the .torrent file is
                              downloaded to the disk, but is not parsed as a
                              torrent and its contents are not downloaded.

                              Possible Values: true, mem, false
                              Default: true
                              Tags: #bittorrent

 --select-file=INDEX...       Set file to download by specifying its index.
                              You can find the file index using the
                              --show-files option. Multiple indexes can be
                              specified by using ',', for example: "3,6".
                              You can also use '-' to specify a range: "1-5".
                              ',' and '-' can be used together.
                              When used with the -M option, index may vary
                              depending on the query(see --metalink-* options).

                              Possible Values: 1-1048576
                              Tags: #metalink, #bittorrent

 --seed-time=MINUTES          Specify seeding time in (fractional) minutes.
                              Also see the --seed-ratio option.

                              Possible Values: 0.0-*
                              Tags: #bittorrent

 --seed-ratio=RATIO           Specify share ratio. Seed completed torrents
                              until share ratio reaches RATIO.
                              You are strongly encouraged to specify equals or
                              more than 1.0 here. Specify 0.0 if you intend to
                              do seeding regardless of share ratio.
                              If --seed-time option is specified along with
                              this option, seeding ends when at least one of
                              the conditions is satisfied.

                              Possible Values: 0.0-*
                              Default: 1.0
                              Tags: #bittorrent

 --peer-id-prefix=PEER_ID_PREFIX Specify the prefix of peer ID. The peer ID in
                              BitTorrent is 20 byte length. If more than 20
                              bytes are specified, only first 20 bytes are
                              used. If less than 20 bytes are specified, random
                              byte data are added to make its length 20 bytes.

                              Default: A2-1-37-0-
                              Tags: #bittorrent

 --peer-agent=PEER_AGENT  Set client reported during Extended torrent handshakes

                              Default: aria2/1.37.0
                              Tags: #bittorrent

 --enable-peer-exchange[=true|false] Enable Peer Exchange extension.

                              Possible Values: true, false
                              Default: true
                              Tags: #bittorrent

 --enable-dht[=true|false]    Enable IPv4 DHT functionality. It also enables
                              UDP tracker support. If a private flag is set
                              in a torrent, aria2 doesn't use DHT for that
                              download even if ``true`` is given.

                              Possible Values: true, false
                              Default: true
                              Tags: #basic, #bittorrent

 --dht-listen-port=PORT...    Set UDP listening port used by DHT(IPv4, IPv6)
                              and UDP tracker. Multiple ports can be specified
                              by using ',', for example: "6881,6885". You can
                              also use '-' to specify a range: "6881-6999".
                              ',' and '-' can be used together.

                              Possible Values: 1024-65535
                              Default: 6881-6999
                              Tags: #basic, #bittorrent

 --dht-entry-point=HOST:PORT  Set host and port as an entry point to IPv4 DHT
                              network.

                              Possible Values: HOST:PORT
                              Tags: #bittorrent

 --dht-file-path=PATH         Change the IPv4 DHT routing table file to PATH.

                              Possible Values: /path/to/file
                              Default: /root/.cache/aria2/dht.dat
                              Tags: #bittorrent

 --enable-dht6[=true|false]   Enable IPv6 DHT functionality.
                              Use --dht-listen-port option to specify port
                              number to listen on. See also --dht-listen-addr6
                              option.

                              Possible Values: true, false
                              Default: false
                              Tags: #basic, #bittorrent

 --dht-listen-addr6=ADDR      Specify address to bind socket for IPv6 DHT. 
                              It should be a global unicast IPv6 address of the
                              host.

                              Tags: #basic, #bittorrent

 --dht-entry-point6=HOST:PORT Set host and port as an entry point to IPv6 DHT
                              network.

                              Possible Values: HOST:PORT
                              Tags: #bittorrent

 --dht-file-path6=PATH        Change the IPv6 DHT routing table file to PATH.

                              Possible Values: /path/to/file
                              Default: /root/.cache/aria2/dht6.dat
                              Tags: #bittorrent

 --bt-min-crypto-level=plain|arc4 Set minimum level of encryption method.
                              If several encryption methods are provided by a
                              peer, aria2 chooses the lowest one which satisfies
                              the given level.

                              Possible Values: plain, arc4
                              Default: plain
                              Tags: #bittorrent

 --bt-require-crypto[=true|false] If true is given, aria2 doesn't accept and
                              establish connection with legacy BitTorrent
                              handshake. Thus aria2 always uses Obfuscation
                              handshake.

                              Possible Values: true, false
                              Default: false
                              Tags: #bittorrent

 --bt-request-peer-speed-limit=SPEED If the whole download speed of every
                              torrent is lower than SPEED, aria2 temporarily
                              increases the number of peers to try for more
                              download speed. Configuring this option with your
                              preferred download speed can increase your
                              download speed in some cases.
                              You can append K or M(1K = 1024, 1M = 1024K).

                              Possible Values: 0-*
                              Default: 50K
                              Tags: #bittorrent

 --bt-max-open-files=NUM      Specify maximum number of files to open in
                              multi-file BitTorrent/Metalink downloads
                              globally.

                              Possible Values: 1-*
                              Default: 100
                              Tags: #bittorrent

 --bt-seed-unverified[=true|false] Seed previously downloaded files without
                              verifying piece hashes.

                              Possible Values: true, false
                              Default: false
                              Tags: #bittorrent

 --bt-hash-check-seed[=true|false] If true is given, after hash check using
                              --check-integrity option and file is complete,
                              continue to seed file. If you want to check file
                              and download it only when it is damaged or
                              incomplete, set this option to false.
                              This option has effect only on BitTorrent
                              download.

                              Possible Values: true, false
                              Default: true
                              Tags: #bittorrent, #checksum

 --bt-max-peers=NUM           Specify the maximum number of peers per torrent.
                              0 means unlimited.
                              See also --bt-request-peer-speed-limit option.

                              Possible Values: 0-*
                              Default: 55
                              Tags: #bittorrent

 --bt-external-ip=IPADDRESS   Specify the external IP address to use in
                              BitTorrent download and DHT. It may be sent to
                              BitTorrent tracker. For DHT, this option should
                              be set to report that local node is downloading
                              a particular torrent. This is critical to use
                              DHT in a private network. Although this function
                              is named 'external', it can accept any kind of IP
                              addresses.

                              Possible Values: a numeric IP address
                              Tags: #bittorrent

 -O, --index-out=INDEX=PATH   Set file path for file with index=INDEX. You can
                              find the file index using the --show-files option.
                              PATH is a relative path to the path specified in
                              --dir option. You can use this option multiple
                              times.

                              Possible Values: INDEX=PATH
                              Tags: #bittorrent

 --bt-tracker-interval=SEC    Set the interval in seconds between tracker
                              requests. This completely overrides interval value
                              and aria2 just uses this value and ignores the
                              min interval and interval value in the response of
                              tracker. If 0 is set, aria2 determines interval
                              based on the response of tracker and the download
                              progress.

                              Possible Values: 0-*
                              Default: 0
                              Tags: #bittorrent

 --bt-stop-timeout=SEC        Stop BitTorrent download if download speed is 0 in
                              consecutive SEC seconds. If 0 is given, this
                              feature is disabled.

                              Possible Values: 0-*
                              Default: 0
                              Tags: #bittorrent

 --bt-prioritize-piece=head[=SIZE],tail[=SIZE] Try to download first and last
                              pieces of each file first. This is useful for
                              previewing files. The argument can contain 2
                              keywords:head and tail. To include both keywords,
                              they must be separated by comma. These keywords
                              can take one parameter, SIZE. For example, if
                              head=SIZE is specified, pieces in the range of
                              first SIZE bytes of each file get higher priority.
                              tail=SIZE means the range of last SIZE bytes of
                              each file. SIZE can include K or M(1K = 1024, 1M =
                              1024K). If SIZE is omitted, SIZE=1M is used.

                              Possible Values: head[=SIZE], tail[=SIZE]
                              Tags: #bittorrent

 --bt-save-metadata[=true|false] Save metadata as .torrent file. This option has
                              effect only when BitTorrent Magnet URI is used.
                              The filename is hex encoded info hash with suffix
                              .torrent. The directory to be saved is the same
                              directory where download file is saved. If the
                              same file already exists, metadata is not saved.
                              See also --bt-metadata-only option.

                              Possible Values: true, false
                              Default: false
                              Tags: #bittorrent

 --bt-metadata-only[=true|false] Download metadata only. The file(s) described
                              in metadata will not be downloaded. This option
                              has effect only when BitTorrent Magnet URI is
                              used. See also --bt-save-metadata option.

                              Possible Values: true, false
                              Default: false
                              Tags: #bittorrent

 --bt-enable-lpd[=true|false] Enable Local Peer Discovery.

                              Possible Values: true, false
                              Default: false
                              Tags: #bittorrent

 --bt-lpd-interface=INTERFACE Use given interface for Local Peer Discovery. If
                              this option is not specified, the default
                              interface is chosen. You can specify interface
                              name and IP address.

                              Possible Values: interface, IP address
                              Tags: #bittorrent

 --bt-tracker-timeout=SEC     Set timeout in seconds.

                              Possible Values: 1-600
                              Default: 60
                              Tags: #bittorrent

 --bt-tracker-connect-timeout=SEC Set the connect timeout in seconds to
                              establish connection to tracker. After the
                              connection is established, this option makes no
                              effect and --bt-tracker-timeout option is used
                              instead.

                              Possible Values: 1-600
                              Default: 60
                              Tags: #bittorrent

 --dht-message-timeout=SEC    Set timeout in seconds.

                              Possible Values: 1-60
                              Default: 10
                              Tags: #bittorrent

 --on-bt-download-complete=COMMAND For BitTorrent, a command specified in
                              --on-download-complete is called after download
                              completed and seeding is over. On the other hand,
                              this option sets the command to be executed after
                              download completed but before seeding.
                              See --on-download-start option for the
                              requirement of COMMAND.

                              Possible Values: /path/to/command
                              Tags: #advanced, #hook

 --bt-tracker=URI[,...]       Comma separated list of additional BitTorrent
                              tracker's announce URI. These URIs are not
                              affected by --bt-exclude-tracker option because
                              they are added after URIs in --bt-exclude-tracker
                              option are removed.

                              Possible Values: URI,...
                              Tags: #bittorrent

 --bt-exclude-tracker=URI[,...] Comma separated list of BitTorrent tracker's
                              announce URI to remove. You can use special value
                              '*' which matches all URIs, thus removes all
                              announce URIs. When specifying '*' in shell
                              command-line, don't forget to escape or quote it.
                              See also --bt-tracker option.

                              Possible Values: URI,... or *
                              Tags: #bittorrent

 --bt-remove-unselected-file[=true|false] Removes the unselected files when
                              download is completed in BitTorrent. To
                              select files, use --select-file option. If
                              it is not used, all files are assumed to be
                              selected. Please use this option with care
                              because it will actually remove files from
                              your disk.

                              Possible Values: true, false
                              Default: false
                              Tags: #bittorrent

 --bt-detach-seed-only[=true|false]
                              Exclude seed only downloads when counting
                              concurrent active downloads (See -j option).
                              This means that if -j3 is given and this option
                              is turned on and 3 downloads are active and one
                              of those enters seed mode, then it is excluded
                              from active download count (thus it becomes 2),
                              and the next download waiting in queue gets
                              started. But be aware that seeding item is still
                              recognized as active download in RPC method.

                              Possible Values: true, false
                              Default: false
                              Tags: #bittorrent

 --bt-force-encryption[=true|false]
                              Requires BitTorrent message payload encryption
                              with arc4. This is a shorthand of
                              --bt-require-crypto --bt-min-crypto-level=arc4.
                              If true is given, deny legacy BitTorrent
                              handshake and only use Obfuscation handshake and
                              always encrypt message payload.

                              Possible Values: true, false
                              Default: false
                              Tags: #bittorrent

 --bt-enable-hook-after-hash-check[=true|false] Allow hook command invocation
                              after hash check (see -V option) in BitTorrent
                              download. By default, when hash check succeeds,
                              the command given by --on-bt-download-complete
                              is executed. To disable this action, give false
                              to this option.

                              Possible Values: true, false
                              Default: true
                              Tags: #bittorrent

 --bt-load-saved-metadata[=true|false]
                              Before getting torrent metadata from DHT when
                              downloading with magnet link, first try to read
                              file saved by --bt-save-metadata option. If it is
                              successful, then skip downloading metadata from
                              DHT.

                              Possible Values: true, false
                              Default: false
                              Tags: #bittorrent

 -M, --metalink-file=METALINK_FILE The file path to the .meta4 and .metalink
                              file. Reads input from stdin when '-' is
                              specified.

                              Possible Values: /path/to/file, -
                              Tags: #basic, #metalink

 --metalink-version=VERSION   The version of the file to download.

                              Tags: #metalink

 --metalink-language=LANGUAGE The language of the file to download.

                              Tags: #metalink

 --metalink-os=OS             The operating system of the file to download.

                              Tags: #metalink

 --metalink-location=LOCATION[,...] The location of the preferred server.
                              A comma-delimited list of locations is
                              acceptable.

                              Tags: #metalink

 --follow-metalink=true|false|mem If true or mem is specified, when a file
                              whose suffix is .meta4 or .metalink, or content
                              type of application/metalink4+xml or
                              application/metalink+xml is downloaded, aria2
                              parses it as a metalink file and downloads files
                              mentioned in it.
                              If mem is specified, a metalink file is not
                              written to the disk, but is just kept in memory.
                              If false is specified, the .metalink file is
                              downloaded to the disk, but is not parsed as a
                              metalink file and its contents are not
                              downloaded.

                              Possible Values: true, mem, false
                              Default: true
                              Tags: #metalink

 --metalink-preferred-protocol=PROTO Specify preferred protocol. Specify 'none'
                              if you don't have any preferred protocol.

                              Possible Values: http, https, ftp, none
                              Default: none
                              Tags: #metalink

 --metalink-enable-unique-protocol[=true|false] If true is given and several
                              protocols are available for a mirror in a metalink
                              file, aria2 uses one of them.
                              Use --metalink-preferred-protocol option to
                              specify the preference of protocol.

                              Possible Values: true, false
                              Default: true
                              Tags: #metalink

 --metalink-base-uri=URI      Specify base URI to resolve relative URI in
                              metalink:url and metalink:metaurl element in a
                              metalink file stored in local disk. If URI points
                              to a directory, URI must end with '/'.

                              Tags: #metalink

Refer to man page for more information.
