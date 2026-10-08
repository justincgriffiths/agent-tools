#!/usr/bin/env bash
# prr.sh — "pr red". Thin wrapper: asks GitHub for every ready PR I authored, its check
# rollup and which checks are red on its base branch, hands the JSON to prr.py, logs the verdict.
#
# Long name: list-ready-pull-requests-whose-ci-is-red
# Judgment + exit-code contract live in prr.py. This file owns the queries and the log.
#
#   exit 0  no ready PR red or pending     exit 1  ready PR(s) red
#   exit 2  query failed                   exit 3  unparseable response
#   exit 4  none red, some still pending
# 2, 3 and 4 all mean UNKNOWN — never report any of them as "green".
#
# Usage:  prr.sh                 # every open, ready PR authored by me, both orgs
#         prr.sh o/r#123 ...     # just these PRs (use before flipping one ready)
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$DIR/prr.log"
ARGV="$*"

log() {
  rc=$1; shift
  printf '[%s] argv=[%s] exit=%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$ARGV" "$rc" "$*" >> "$LOG"
}

if [ $# -gt 0 ]; then
  targets="$(printf '%s\n' "$@")"
else
  targets="$(gh search prs --author @me --state open --draft=false \
              --json repository,number --limit 100 \
              --jq '.[] | "\(.repository.nameWithOwner)#\(.number)"' 2>&1)"
  rc=$?
  if [ $rc -ne 0 ]; then
    log 2 "search failed: $(printf '%s' "$targets" | tr '\n' ' ' | cut -c1-200)"
    echo "UNKNOWN: gh search failed — this is not 'all green'." >&2
    exit 2
  fi
fi

json="["; sep=""
while IFS= read -r t; do
  [ -n "$t" ] || continue
  repo="${t%%#*}" num="${t##*#}"
  pr="$(gh pr view "$num" -R "$repo" --json number,title,url,baseRefName,isDraft,statusCheckRollup 2>&1)" \
    || { log 2 "pr view $t failed"; echo "UNKNOWN: gh pr view $t failed." >&2; exit 2; }
  [ "$(printf '%s' "$pr" | python3 -c 'import json,sys; print(json.load(sys.stdin)["isDraft"])')" = "True" ] && continue
  base="$(printf '%s' "$pr" | python3 -c 'import json,sys; print(json.load(sys.stdin)["baseRefName"])')"
  # checks red on the base branch's head: the LATEST run of each check name (a head can carry
  # several runs per name, e.g. nightly re-runs) + commit statuses (already latest per context)
  base_red="$( { gh api "repos/$repo/commits/$base/check-runs?per_page=100" \
                   --jq '.check_runs | group_by(.name) | map(max_by(.completed_at // "")) | .[]
                         | select(.conclusion=="failure" or .conclusion=="cancelled" or .conclusion=="timed_out") | .name';
                 gh api "repos/$repo/commits/$base/status" \
                   --jq '.statuses[] | select(.state=="failure" or .state=="error") | .context'; } 2>/dev/null \
               | python3 -c 'import json,sys; print(json.dumps(sorted({l.strip() for l in sys.stdin if l.strip()})))')"
  json+="$sep$(printf '%s' "$pr" | python3 -c '
import json, sys
p = json.load(sys.stdin)
print(json.dumps({"repo": sys.argv[1], "number": p["number"], "title": p["title"], "url": p["url"],
                  "base": p["baseRefName"], "checks": p.get("statusCheckRollup") or [],
                  "base_red": json.loads(sys.argv[2])}))' "$repo" "$base_red")"
  sep=","
done <<< "$targets"
json+="]"

printf '%s' "$json" | python3 "$DIR/prr.py"
rc=$?
case $rc in
  0) verdict=clean ;;
  1) verdict=ready-red ;;
  4) verdict=pending ;;
  *) verdict=unknown ;;
esac
log "$rc" "verdict=$verdict"
exit $rc
