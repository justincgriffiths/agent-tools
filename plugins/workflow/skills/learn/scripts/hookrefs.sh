#!/usr/bin/env bash
# hookrefs.sh — lint every ~/.claude/hooks path a skill cites (long name: hook-reference-lint).
#
# One job: find hook citations in a skill library that point at nothing. Filter — reads the
# library and ~/.claude, writes findings to stdout, touches nothing but its own .log line.
#
#   usage: hookrefs.sh [LIBRARY_DIR]      default: the skills directory this script lives in
#
# Scans <lib>/*/SKILL.md and <lib>/*/references/**/*.md for ~/.claude/hooks/<name>,
# $HOME/.claude/hooks/<name> and ${HOME}/.claude/hooks/<name>. One line per finding:
#
#   <skill>:<file>:<line> MISSING  ~/.claude/hooks/<name>   no such file
#   <skill>:<file>:<line> NOT-EXEC ~/.claude/hooks/<name>   file exists, exec bit unset
#   <skill>:<file>:<line> UNWIRED  ~/.claude/hooks/<name>   no hooks[].command in
#                                  ~/.claude/settings.json (or settings.local.json) names it
#
# Not checked: placeholders (a name holding < > { } * $ or ...), a bare ~/.claude/hooks/, and
# NOT-EXEC/UNWIRED for files that are not hooks themselves — data files a hook reads
# (.tsv .csv .json .jsonl .yml .yaml .txt .md .log), *.test.* files, and directories. Those
# only have to exist. A placeholder is skipped wherever it sits; fenced code is NOT skipped.
#
# Exit code is the verdict: 0 = clean, 1 = findings, 2 = usage error or bug (missing library,
# no jq, unparseable settings). No ~/.claude at all (CI runners) prints a skip notice to stderr
# and exits 0. Each run appends one line to the sibling hookrefs.log (HOOKREFS_LOG overrides).
#
# Why: a skill cited a ~/.claude/hooks/ write-guard as its enforcement for two months while
# the file did not exist and nothing in settings.json wired it; learn/references/routing-rules.md
# had held it up as the working example.
set -uo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="${HOOKREFS_LOG:-$DIR/hookrefs.log}"
ARGS="$*"
FILES=0; REFS=0; HITS=0

finish() { # $1=exit code, $2=note — the code is captured before $(date) runs, never after
  local rc="$1"
  printf '[%s] argv=[%s] exit=%s files=%s refs=%s findings=%s note="%s"\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$ARGS" "$rc" "$FILES" "$REFS" "$HITS" "$2" >>"$LOG" 2>/dev/null
  exit "$rc"
}

case "${1:-}" in -h|--help) sed -n '2,26p' "$0"; exit 0 ;; esac
[ "$#" -le 1 ] || { echo "usage: hookrefs.sh [LIBRARY_DIR]" >&2; finish 2 "too many args"; }

LIB="${1:-$(cd "$DIR/../.." && pwd)}"
[ -d "$LIB" ] || { echo "hookrefs: no such library: $LIB" >&2; finish 2 "missing library"; }
LIB="$(cd "$LIB" && pwd)"

CD="$HOME/.claude"
if [ ! -d "$CD" ]; then
  echo "hookrefs: skip — no $CD on this host (CI runner?); nothing to check against" >&2
  finish 0 "skipped: no ~/.claude"
fi
command -v jq >/dev/null 2>&1 || { echo "hookrefs: jq not on PATH" >&2; finish 2 "no jq"; }

# Every hook command wired in settings, one per line. A settings file that exists but does
# not parse is a bug to surface, not a reason to call every hook unwired.
WIRED=""
for s in "$CD/settings.json" "$CD/settings.local.json"; do
  [ -f "$s" ] || continue
  cmds="$(jq -r '(.hooks // {}) | .. | objects | select(has("command")) | .command | strings' "$s" 2>/dev/null)" \
    || { echo "hookrefs: cannot parse $s" >&2; finish 2 "bad json: $s"; }
  WIRED="$WIRED$cmds"$'\n'
done

# 0 if some wired command names .claude/hooks/<rel> as a whole token (so copy-guard.sh is not
# satisfied by copy-guard-bash.sh, nor x.sh by x.sh.bak).
is_wired() {
  printf '%s' "$WIRED" | awk -v n=".claude/hooks/$1" '
    { s = $0
      while ((i = index(s, n)) > 0) {
        c = substr(s, i + length(n), 1)
        if (c == "" || c ~ /[[:space:]"'"'"';&|)]/) { found = 1; exit }
        s = substr(s, i + 1)
      } }
    END { exit found ? 0 : 1 }'
}

# Files that must exist but are not hooks: no exec bit or wiring expected.
needs_wiring() {
  case "$1" in
    */) return 1 ;;
    *.test.*) return 1 ;;
    *.tsv|*.csv|*.json|*.jsonl|*.yml|*.yaml|*.txt|*.md|*.log) return 1 ;;
  esac
  [ -d "$CD/hooks/$1" ] && return 1
  return 0
}

PAT='(~|\$HOME|\$\{HOME\})/\.claude/hooks/[^][:space:]`'"'"'"()|,;]*'
LIST="$(mktemp)"; trap 'rm -f "$LIST"' EXIT
{ find "$LIB" -mindepth 2 -maxdepth 2 -name SKILL.md -not -path '*/.git/*'
  find "$LIB" -mindepth 3 -path "$LIB/*/references/*" -name '*.md' -not -path '*/.git/*'
} 2>/dev/null | LC_ALL=C sort >"$LIST"

while IFS= read -r f; do
  [ -f "$f" ] || continue
  rel="${f#"$LIB"/}"; skill="${rel%%/*}"; sub="${rel#*/}"
  case "$sub" in SKILL.md|references/*) ;; *) continue ;; esac   # find's * spans dirs
  FILES=$((FILES + 1))
  while IFS= read -r hit; do
    [ -n "$hit" ] || continue
    ln="${hit%%:*}"; cited="${hit#*:}"
    name="${cited#*/.claude/hooks/}"
    while :; do case "$name" in *.|*:) name="${name%?}" ;; *) break ;; esac; done
    [ -n "$name" ] || continue                                    # bare ~/.claude/hooks/
    case "$name" in *'<'*|*'>'*|*'{'*|*'}'*|*'*'*|*'$'*|*...*|*…*) continue ;; esac
    REFS=$((REFS + 1))
    shown="~/.claude/hooks/$name"; path="$CD/hooks/${name%/}"
    if [ ! -e "$path" ]; then
      echo "$skill:$sub:$ln MISSING $shown"; HITS=$((HITS + 1)); continue
    fi
    needs_wiring "$name" || continue
    if [ ! -x "$path" ]; then echo "$skill:$sub:$ln NOT-EXEC $shown"; HITS=$((HITS + 1)); fi
    if ! is_wired "$name"; then echo "$skill:$sub:$ln UNWIRED $shown"; HITS=$((HITS + 1)); fi
  done <<EOF
$(grep -noE "$PAT" "$f" 2>/dev/null)
EOF
done <"$LIST"

[ "$HITS" -eq 0 ] && finish 0 "clean"
finish 1 "findings"
