#!/bin/bash

set -e

cmd="$@"


DIRSELF=$(cd $(dirname $0); pwd -P)

$DIRSELF/preflight-db.sh
$DIRSELF/preflight-static.sh

exec $cmd