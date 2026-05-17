#!/usr/bin/env bash
# Usage: scopus_search.sh "<query>" [view]
#   <query>: Scopus query string, e.g. 'DOI(10.1111/x.y)' or 'TITLE("foo") AND PUBYEAR IS 2020'
#   view:    STANDARD (default) or COMPLETE (needs SCOPUS_INST_TOKEN)
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

if [ -z "${SCOPUS_API_KEY:-}" ]; then
    echo "Error: SCOPUS_API_KEY is not set in $SKILL_DIR/.env" >&2
    exit 1
fi

if [ $# -lt 1 ]; then
    echo "Usage: $0 \"<query>\" [view]" >&2
    exit 2
fi

query="$1"
view="${2:-STANDARD}"

headers=(-H "X-ELS-APIKey: $SCOPUS_API_KEY" -H "Accept: application/json")
if [ -n "${SCOPUS_INST_TOKEN:-}" ]; then
    headers+=(-H "X-ELS-Insttoken: $SCOPUS_INST_TOKEN")
fi

curl -sG "https://api.elsevier.com/content/search/scopus" \
    "${headers[@]}" \
    --data-urlencode "query=$query" \
    --data-urlencode "view=$view" \
    --data-urlencode "count=5"
