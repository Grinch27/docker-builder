#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apk add --no-cache git make build-base
git clone --branch master --single-branch https://github.com/Wind4/vlmcsd.git
cd vlmcsd/
make

cp bin/vlmcsd /usr/bin/vlmcsd

# /usr/bin/vlmcsd -D -d
vlmcsd -V

version=$(vlmcsd -V)
remove_prefix="vlmcsd "
remove_suffix=", built"

version=${version##*$remove_prefix}
version=${version%%$remove_suffix*}
echo "version=${version}"

# Usage:
#    /usr/bin/vlmcsd [ options ]
# Where:
#   -u <user>		set uid to <user>
#   -g <group>		set gid to <group>
#   -a <csvlk>=<epid>	use <epid> for <csvlk>
#   -r 0|1|2		set ePID randomization level (default 1)
#   -C <LCID>		use fixed <LCID> in random ePIDs
#   -H <build>		use fixed <build> number in random ePIDs
#   -o 0|1|2|3		set protection level against clients with public IP addresses (default 0)
#   -x <level>		exit if warning <level> reached (default 0)
#   -L <address>[:<port>]	listen on IP address <address> with optional <port>
#   -P <port>		set TCP port <port> for subsequent -L statements (default 1688)
#   -F0, -F1		disable/enable binding to foreign IP addresses
#   -m <clients>		Handle max. <clients> simultaneously (default no limit)
#   -e			log to stdout
#   -D			run in foreground
#   -K 0|1|2|3		set white-listing level for KMS IDs (default -K0)
#   -c0, -c1		disable/enable client time checking (default -c0)
#   -M0, -M1		disable/enable maintaining clients (default -M0)
#   -E0, -E1		disable/enable start with empty client list (default -E0, ignored if -M0)
#   -t <seconds>		disconnect clients after <seconds> of inactivity (default 30)
#   -d			disconnect clients after each request
#   -k			don't disconnect clients after each request (default)
#   -N0, -N1		disable/enable NDR64
#   -B0, -B1		disable/enable bind time feature negotiation
#   -p <file>		write pid to <file>
#   -i <file>		use config file <file>
#   -j <file>		use KMS data file <file>
#   -R <interval>		renew activation every <interval> (default 1w)
#   -A <interval>		retry activation every <interval> (default 2h)
#   -l syslog		log to syslog
#   -l <file>		log to <file>
#   -T0, -T1		disable/enable logging with time and date (default -T1)
#   -v			log verbose
#   -q			don't log verbose (default)
#   -V			display version information and exit
