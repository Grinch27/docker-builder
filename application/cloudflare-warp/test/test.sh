#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

version=$(warp-cli --version)
remove_prefix="warp-cli "
version=${version##*$remove_prefix}
echo "version=${version}"

# (base) user@user:~$ warp-cli
# CLI to the WARP service daemon

# Usage: warp-cli [OPTIONS] <COMMAND>

# Commands:
#   connect               Maintain a connection whenever possible
#   debug                 Debugging commands
#   disconnect            Disconnect the client
#   dns                   Configure DNS settings
#   environment           Configure the WARP Client's compliance environment
#   mdm                   MDM configs
#   mode                  Set the client's general operating mode
#   override              Allow temporary overrides of administrative settings
#   proxy                 Configure proxy mode settings
#   registration          Registration settings
#   connector             Register a WARP Connector
#   settings              Show or alter general application settings
#   status                Return the current connection status
#   target                Manage targets
#   trusted               Configure trusted networks where the client will be automatically disabled (Consumer only)
#   tunnel                Configure tunnel settings
#   vnet                  Get or specify connected virtual network
#   generate-completions  Generate completions for a given shell and print to stdout
#   stats                 Display statistics for Cloudflare WARP
#   certs                 Print all account certificates installed on the device to stdout
#   help                  Print this message or the help of the given subcommand(s)

# Options:
#   -l, --listen       Listen for status changes and DNS logs (if enabled)
#       --accept-tos   Accept the Terms of Service agreement
#   -v, --verbose...   Enable verbose output. Multiple "v"s adds more verbosity
#   -j, --json         Pretty print output as json
#       --no-paginate  Disable automatic pagination
#       --no-ansi      Disable ANSI characters in standard outputs
#   -h, --help         Print help (see more with '--help')
#   -V, --version      Print version
