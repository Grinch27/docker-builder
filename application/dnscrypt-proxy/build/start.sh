#!/bin/sh

set -e

exec dnscrypt-proxy --config /etc/dnscrypt-proxy/dnscrypt-proxy.toml
