#!/usr/bin/env bash
# Usage: wos_search.sh "<query>"
#   <query>: WoS Starter query string, e.g. 'DO=10.1111/x.y' or 'TI="foo" AND PY=2020'
# Keys are sourced from ../.env (skill-local).
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ ! -f "$SKILL_DIR/.env" ]; then
    echo "Error: $SKILL_DIR/.env not found. Copy .env.example to .env and fill in keys." >&2
    exit 1
fi
set -a
# shellcheck disable=SC1090
source "$SKILL_DIR/.env"
set +a

if [ -z "${WOS_API_KEY:-}" ]; then
    echo "Error: WOS_API_KEY is not set in $SKILL_DIR/.env" >&2
    exit 1
fi

if [ $# -lt 1 ]; then
    echo "Usage: $0 \"<query>\"" >&2
    exit 2
fi

query="$1"

curl -sG "https://api.clarivate.com/apis/wos-starter/v1/documents" \
    -H "X-ApiKey: $WOS_API_KEY" \
    -H "Accept: application/json" \
    --data-urlencode "db=WOS" \
    --data-urlencode "q=$query" \
    --data-urlencode "limit=5"
