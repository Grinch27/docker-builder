# warp-cli 完整使用说明（自动抓取）

- 版本: warp-cli 2026.4.1390.0
- 生成时间: 2026-06-07T15:37:49+08:00

## warp-cli connect
- 摘要:               Maintain a connection whenever possible

```
Maintain a connection whenever possible

Usage: warp-cli connect [OPTIONS]

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli debug
- 摘要:                 Debugging commands

```
Debugging commands

Usage: warp-cli debug [OPTIONS] <COMMAND>

Commands:
  access-reauth              Force refresh authentication with Cloudflare Access
  alternate-network          Get the name of the currently detected alternate network, if any
  connectivity-check         Enable or disable connectivity checks
  dex                        Get the most recently uploaded DEX data. Returns the most recent test for each dex metric
  network                    Display the current network information
  posture                    Display the most recent device posture information
  pcap                       Run a packet capture on the device
  speed-test                 Run a speed test on the device
  qlog                       Enable qlog logging on the tunnel, if supported by the tunnel protocol
  frequent-connection-stats  Enable frequent connection stats for the QUIC connection for 1 hour
  help                       Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli disconnect
- 摘要:            Disconnect the client

```
Disconnect the client

Usage: warp-cli disconnect [OPTIONS]

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli dns
- 摘要:                   Configure DNS settings

```
Configure DNS settings

Usage: warp-cli dns [OPTIONS] <COMMAND>

Commands:
  fallback           Configure fallback domains
  families           Configure Families Mode settings (Consumer only)
  gateway-id         Force the app to use the specified Gateway ID for DNS queries
  log                Enable/Disable DNS logging
  stats              Retrieve DNS stats for the current connection
  default-fallbacks  Display which DNS servers are being used for default fallback
  help               Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli environment
- 摘要:           Configure the WARP Client's compliance environment

```
Configure the WARP Client's compliance environment

Usage: warp-cli environment [OPTIONS] <COMMAND>

Commands:
  set    Set the client's compliance environment
  reset  Reset the client's compliance environment override
  help   Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli mdm
- 摘要:                   MDM configs

```
MDM configs

Usage: warp-cli mdm [OPTIONS] <COMMAND>

Commands:
  get-configs  Show information about current MDM configurations
  set-config   Apply config from configs found in MDM file
  refresh      Immediately refresh MDM configuration from the local policy file
  help         Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli mode
- 摘要:                  Set the client's general operating mode

```
Set the client's general operating mode

Usage: warp-cli mode [OPTIONS] <MODE>

Arguments:
  <MODE>
          Possible values:
          - warp:        Establish a tunnel and use normal UDP DNS proxying
          - doh:         Do not establish a tunnel. Only proxy DNS over DoH
          - warp+doh:    Establish a tunnel and use DoH for DNS
          - dot:         Do not establish a tunnel. Only proxy DNS over DoT
          - warp+dot:    Establish a tunnel and use DoT for DNS
          - proxy:       Establish a tunnel for use in a SOCKS5 proxy
          - tunnel_only: Establish a tunnel and do not proxy DNS

Options:
      --no-paginate
          Disable automatic pagination

  -h, --help
          Print help (see a summary with '-h')
```

## warp-cli override
- 摘要:              Allow temporary overrides of administrative settings

```
Allow temporary overrides of administrative settings

Usage: warp-cli override [OPTIONS] <CODE>
       warp-cli override <COMMAND>

Commands:
  show           Return information about any currently applied administrative override
  unlock         Temporarily override policies that require the client to stay enabled
  local-network  Override settings to access the local area network
  help           Print this message or the help of the given subcommand(s)

Arguments:
  <CODE>  

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli proxy
- 摘要:                 Configure proxy mode settings

```
Configure proxy mode settings

Usage: warp-cli proxy [OPTIONS] <COMMAND>

Commands:
  port  Override the listening port for proxy mode (127.0.0.1:{port})
  help  Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli registration
- 摘要:          Registration settings

```
Registration settings

Usage: warp-cli registration [OPTIONS] <COMMAND>

Commands:
  show          Show information about the current registration
  new           Register this client (Must be run before first connection!)
  delete        Delete current registration
  organization  Get the name of the current Teams organization
  devices       Display the list of devices associated with the current registration (Consumer only)
  license       Attach the current registration to a different account using a license key (Consumer only)
  help          Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli connector
- 摘要:             Register a WARP Connector

```
Register a WARP Connector

Usage: warp-cli connector [OPTIONS] <COMMAND>

Commands:
  new   Register a new WARP Connector
  help  Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli settings
- 摘要:              Show or alter general application settings

```
Show or alter general application settings

Usage: warp-cli settings [OPTIONS]
       warp-cli settings <COMMAND>

Commands:
  list                 Retrieve the current application settings
  reset                Restore settings to default
  support-url          Get the support url for the current Teams organization
  mode-switch-allowed  Outputs true if Teams users should be able to change connection mode, or false if not
  help                 Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli status
- 摘要:                Return the current connection status

```
Return the current connection status

Usage: warp-cli status [OPTIONS]

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli target
- 摘要:                Manage targets

```
Manage targets

Usage: warp-cli target [OPTIONS] <COMMAND>

Commands:
  list  List all available targets accessible by the current user
  help  Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli trusted
- 摘要:               Configure trusted networks where the client will be automatically disabled (Consumer only)

```
Configure trusted networks where the client will be automatically disabled (Consumer only)

Usage: warp-cli trusted [OPTIONS] <COMMAND>

Commands:
  ssid      Configure trusted Wi-Fi networks for which the client will be automatically disconnected (Consumer only)
  ethernet  Automatically disconnect on all ethernet networks (Consumer only)
  wifi      Automatically disconnect on all Wi-Fi networks (Consumer only)
  help      Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli tunnel
- 摘要:                Configure tunnel settings

```
Configure tunnel settings

Usage: warp-cli tunnel [OPTIONS] <COMMAND>

Commands:
  dump            Get split tunnel routing dump. For include-only mode, this shows routes NOT included
  host            Configure split tunnel hosts
  ip              Configure split tunnel IPs
  stats           Retrieve the stats for the current tunnel connection
  rotate-keys     Generate a new key-pair, keeping the current registration
  endpoint        Force the client to connect to the specified IP:PORT endpoint (Zero Trust customers must run this command as a privileged user)
  protocol        Modify the preferred tunnel protocol (Consumer only)
  masque-options  Modify the MASQUE tunnel protocol options (Consumer only)
  help            Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli vnet
- 摘要:                  Get or specify connected virtual network

```
Get or specify connected virtual network

Usage: warp-cli vnet [OPTIONS] [VNET]

Arguments:
  [VNET]  

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli generate-completions
- 摘要:  Generate completions for a given shell and print to stdout

```
Generate completions for a given shell and print to stdout

Usage: warp-cli generate-completions [OPTIONS] <SHELL>

Arguments:
  <SHELL>  [possible values: bash, elvish, fish, powershell, zsh]

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli stats
- 摘要:                 Display statistics for Cloudflare WARP

```
Display statistics for Cloudflare WARP

Usage: warp-cli stats [OPTIONS] [COMMAND]

Commands:
  enhanced  Display enhanced histogram statistics with full distribution data
  help      Print this message or the help of the given subcommand(s)

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli certs
- 摘要:                 Print all account certificates installed on the device to stdout

```
Print all account certificates installed on the device to stdout

Usage: warp-cli certs [OPTIONS]

Options:
      --no-paginate  Disable automatic pagination
  -h, --help         Print help
```

## warp-cli help
- 摘要:                  Print this message or the help of the given subcommand(s)

```
Print this message or the help of the given subcommand(s)

Usage: warp-cli help [COMMAND]...

Arguments:
  [COMMAND]...  Print help for the subcommand(s)
```

