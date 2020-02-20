#! /bin/bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

if [ $# != 1 ]; then 
    >&2 echo "Usage: `basename $0` host_name"
    exit 1
fi

host=$1
NEW_CONFIG_NAME="/tmp/$host.config"

scp $host:.kube/config $NEW_CONFIG_NAME > /dev/null
CONFIG_PAYLOAD="$($DIR/kube-config-replacer.py $host $NEW_CONFIG_NAME)\n"
diff -u ~/.kube/config <(printf "$CONFIG_PAYLOAD") || true

printf "  Please type 'yes' to continue.\n  > "
read yes
if [ "$yes" != "yes" ]; then 
    printf " Abort sync kube config"
    exit 1; 
fi

printf "$CONFIG_PAYLOAD" > ~/.kube/config
printf "  Done\n"
