#!/usr/bin/env bash
# scan-tree.sh — compare a CANONICAL tree against a VENDORED copy and emit a
# human-reviewable dedup report.
#
# Long name: dedupe-scan-canonical-vs-vendored-tree
#
# Usage:
#   scan-tree.sh --canonical <dir> --vendored <dir> [--name <family>] [--out <dir>]
#
# Emits two artifacts:
#   <out>/YYYY-MM-DD-<family>.md   human-first review report (the product)
#   <out>/YYYY-MM-DD-<family>.tsv  machine-readable verdict rows (the audit trail)
#
# Exit codes: 0 = scan completed (findings are NOT an error), 2 = bad usage/missing dir.
# Log: appends one line per invocation to <script-dir>/scan-tree.log
#
# This script NEVER writes to, moves, or deletes anything in either tree.
set -uo pipefail

export LC_ALL=C   # keep sort collation consistent with join
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SCRIPT_DIR/scan-tree.log"
CANON="" ; VEND="" ; FAMILY="" ; OUTDIR=""

log_line() {
  printf '[%s] argv=[%s] exit=%s %s\n' \
    "$(date -u +%FT%TZ)" "$ORIG_ARGV" "${1:-?}" "${2:-}" >> "$LOG"
}
ORIG_ARGV="$*"

die() { echo "ERROR: $*" >&2; log_line 2 "error=\"$*\""; exit 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --canonical) CANON="${2:-}"; shift 2 ;;
    --vendored)  VEND="${2:-}";  shift 2 ;;
    --name)      FAMILY="${2:-}"; shift 2 ;;
    --out)       OUTDIR="${2:-}"; shift 2 ;;
    -h|--help)   sed -n '2,20p' "$0"; exit 0 ;;
    *) die "unknown arg: $1" ;;
  esac
done

[ -n "$CANON" ] && [ -n "$VEND" ] || die "need --canonical <dir> --vendored <dir>"
[ -d "$CANON" ] || die "canonical dir not found: $CANON"
[ -d "$VEND" ]  || die "vendored dir not found: $VEND"

FAMILY="${FAMILY:-$(basename "$VEND")}"
OUTDIR="${OUTDIR:-$PWD/data/dedupe}"
mkdir -p "$OUTDIR" || die "cannot create out dir: $OUTDIR"

TODAY="$(date +%F)"
REPORT="$OUTDIR/$TODAY-$FAMILY.md"
TSV="$OUTDIR/$TODAY-$FAMILY.tsv"
TMP="$(mktemp -d)"
# Without -e set, a failed mktemp leaves TMP empty and "$TMP/canon.tsv" becomes /canon.tsv.
[ -n "$TMP" ] && [ -d "$TMP" ] || die "mktemp -d failed — refusing to write to filesystem root"
trap 'rm -rf "$TMP"' EXIT

# Noise we never diff: VCS internals, agent config, OS cruft, build output.
prune_and_hash() {
  local root="$1" out="$2"
  ( cd "$root" && find . -type f \
      ! -path '*/.git/*' ! -name '.DS_Store' \
      ! -path '*/node_modules/*' ! -path '*/__pycache__/*' \
      ! -path '*/.claude/*' ! -path '*/out/*' ! -path '*/dist/*' \
      ! -name 'VENDORED.yml' \
      -print0 2>/dev/null \
    | xargs -0 shasum -a 1 2>/dev/null ) \
    | awk '{h=$1; sub(/^[^ \t]+[ \t]+/,""); print $0"\t"h}' | sort > "$out"
}

# Render a path with $HOME collapsed to a literal tilde (readability in the report).
short() { printf '%s' "${1/#$HOME/~}"; }

prune_and_hash "$CANON" "$TMP/canon.tsv"
prune_and_hash "$VEND"  "$TMP/vend.tsv"

N_CANON=$(wc -l < "$TMP/canon.tsv" | tr -d ' ')
N_VEND=$(wc -l < "$TMP/vend.tsv" | tr -d ' ')

# Verdicts. join on relative path (field 1).
join -t "$(printf '\t')" -j 1 "$TMP/vend.tsv" "$TMP/canon.tsv" 2>/dev/null \
  | awk -F'\t' '$2==$3 {print "IDENTICAL\t"$1}' > "$TMP/identical.tsv"
join -t "$(printf '\t')" -j 1 "$TMP/vend.tsv" "$TMP/canon.tsv" 2>/dev/null \
  | awk -F'\t' '$2!=$3 {print "DRIFTED\t"$1}'   > "$TMP/drifted.tsv"
join -t "$(printf '\t')" -v1 -j 1 "$TMP/vend.tsv" "$TMP/canon.tsv" 2>/dev/null \
  | awk -F'\t' '{print "ORPHAN\t"$1}'           > "$TMP/orphan.tsv"
join -t "$(printf '\t')" -v2 -j 1 "$TMP/vend.tsv" "$TMP/canon.tsv" 2>/dev/null \
  | awk -F'\t' '{print "UPSTREAM-ONLY\t"$1}'    > "$TMP/upstream.tsv"

N_ID=$(wc -l < "$TMP/identical.tsv" | tr -d ' ')
N_DR=$(wc -l < "$TMP/drifted.tsv"   | tr -d ' ')
N_OR=$(wc -l < "$TMP/orphan.tsv"    | tr -d ' ')
N_UP=$(wc -l < "$TMP/upstream.tsv"  | tr -d ' ')

cat "$TMP/drifted.tsv" "$TMP/orphan.tsv" "$TMP/identical.tsv" "$TMP/upstream.tsv" > "$TSV"

# Provenance stamp present in the vendored copy?
STAMP="absent"
[ -f "$VEND/VENDORED.yml" ] && STAMP="present"

# ---- human-first report -----------------------------------------------------
{
  echo "# Dedup review — $FAMILY"
  echo
  echo "**Scanned** $TODAY · **canonical** \`$(short "$CANON")\` ($N_CANON files) · **vendored** \`$(short "$VEND")\` ($N_VEND files) · **provenance stamp** $STAMP"
  echo
  echo "## Your call is needed on $((N_DR + N_OR)) files"
  echo
  echo "| Verdict | Files | What it means | Default disposition |"
  echo "|---|---:|---|---|"
  echo "| DRIFTED | $N_DR | Same path, different content. Someone edited one side. | **Read the diff below and pick a winner.** |"
  echo "| ORPHAN | $N_OR | Exists only in the vendored copy. Deleting loses it. | **Rescue upstream or explicitly discard.** |"
  echo "| IDENTICAL | $N_ID | Byte-identical both sides. | Safe to re-vendor from canonical. No review. |"
  echo "| UPSTREAM-ONLY | $N_UP | In canonical, not vendored. Usually just out of scope. | Confirm the allowlist is intentional. |"
  echo
  if [ "$N_DR" -eq 0 ] && [ "$N_OR" -eq 0 ]; then
    echo "> **Nothing needs your review.** The vendored copy is a clean subset of canonical."
    echo "> Re-vendoring is safe and loses nothing."
    echo
  fi

  if [ "$N_DR" -gt 0 ]; then
    echo "## DRIFTED — pick a winner per file"
    echo
    echo "Mark each row: \`canonical\` (overwrite the vendored copy) · \`vendored\` (backport upstream) · \`both\` (needs a manual merge)."
    echo
    echo "| # | File | Vendored | Canonical | Looks like | Winner |"
    echo "|---:|---|---:|---:|---|---|"
    i=0
    while IFS=$'\t' read -r _ f; do
      i=$((i+1))
      vl=$(wc -l < "$VEND/$f" 2>/dev/null | tr -d ' ')
      cl=$(wc -l < "$CANON/$f" 2>/dev/null | tr -d ' ')
      vd=$(date -r "$VEND/$f" +%F 2>/dev/null)
      cd_=$(date -r "$CANON/$f" +%F 2>/dev/null)
      vs=$(date -r "$VEND/$f" +%s 2>/dev/null); cs=$(date -r "$CANON/$f" +%s 2>/dev/null)
      # Heuristic ONLY — mtime is not provenance. Never auto-applied.
      if   [ "${cs:-0}" -gt "${vs:-0}" ] && [ "${cl:-0}" -ge "${vl:-0}" ]; then hint="vendored is stale"
      elif [ "${vs:-0}" -gt "${cs:-0}" ] && [ "${vl:-0}" -ge "${cl:-0}" ]; then hint="vendored edited later"
      else hint="**genuine fork**"; fi
      echo "| $i | \`${f#./}\` | ${vl}L · $vd | ${cl}L · $cd_ | $hint | _______ |"
    done < "$TMP/drifted.tsv"
    echo
    echo "### Diffs"
    echo
    i=0
    while IFS=$'\t' read -r _ f; do
      i=$((i+1))
      echo "<details><summary><strong>$i. ${f#./}</strong></summary>"
      echo
      echo '```diff'
      diff -u "$VEND/$f" "$CANON/$f" 2>/dev/null \
        | sed -e "1s|.*|--- vendored/${f#./}|" -e "2s|.*|+++ canonical/${f#./}|" | head -120
      echo '```'
      echo
      echo "</details>"
      echo
    done < "$TMP/drifted.tsv"
  fi

  if [ "$N_OR" -gt 0 ]; then
    echo "## ORPHAN — only in the vendored copy"
    echo
    echo "These would be **lost** if the vendored dir were replaced from canonical."
    echo
    echo "| File | Lines | Modified |"
    echo "|---|---:|---|"
    while IFS=$'\t' read -r _ f; do
      echo "| \`${f#./}\` | $(wc -l < "$VEND/$f" 2>/dev/null | tr -d ' ') | $(date -r "$VEND/$f" +%F 2>/dev/null) |"
    done < "$TMP/orphan.tsv"
    echo
  fi

  echo "## Reproduce"
  echo
  echo '```'
  echo "\${CLAUDE_PLUGIN_ROOT}/skills/dedupe/scripts/scan-tree.sh \\"
  echo "  --canonical $(short "$CANON") --vendored $(short "$VEND") --name $FAMILY"
  echo '```'
  echo
  echo "Machine-readable verdicts: \`$(short "$TSV")\`"
} > "$REPORT"

# Without -e, a failed report write would still print success and log exit=0.
[ -s "$REPORT" ] || die "report was not written or is empty: $REPORT"

echo "report: $REPORT"
echo "verdicts: $TSV"
printf 'identical=%s drifted=%s orphan=%s upstream-only=%s stamp=%s\n' \
  "$N_ID" "$N_DR" "$N_OR" "$N_UP" "$STAMP"

log_line 0 "family=$FAMILY identical=$N_ID drifted=$N_DR orphan=$N_OR upstream_only=$N_UP stamp=$STAMP report=\"$REPORT\""
