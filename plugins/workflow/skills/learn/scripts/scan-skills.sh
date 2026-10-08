#!/usr/bin/env bash
# scan-skills.sh — inventory the user-authored skill library for the /learn Mode B audit.
# Prints one row per skill: name | SKILL.md line count | resource dirs | first ~40 words of description.
# Deterministic input to the hygiene heuristics — avoids re-deriving the inventory by hand each run.
# Usage: scan-skills.sh [<skill-library-dir>]   (default: $SKILL_LIBRARY, else ~/.claude/skills)
set -euo pipefail

LIB="${1:-${SKILL_LIBRARY:-$HOME/.claude/skills}}"

if [[ ! -d "$LIB" ]]; then
  echo "skill library not found at: $LIB" >&2
  exit 1
fi

printf '%-22s | %5s | %-18s | %s\n' "NAME" "LINES" "RESOURCES" "DESCRIPTION (first ~40 words)"
printf '%s\n' "------------------------------------------------------------------------------------------------"

for dir in "$LIB"/*/; do
  name="$(basename "$dir")"
  skill="$dir/SKILL.md"

  if [[ ! -f "$skill" ]]; then
    # Shared-asset dirs (e.g. *-common) have no SKILL.md — flag, don't audit.
    printf '%-22s | %5s | %-18s | %s\n' "$name" "-" "(no SKILL.md)" "shared assets / not a triggerable skill"
    continue
  fi

  lines="$(wc -l < "$skill" | tr -d ' ')"

  # Resource dirs present (scripts/ references/ assets/ evals/ workflows/).
  res=""
  for r in scripts references assets evals workflows; do
    [[ -d "$dir/$r" ]] && res+="${r%s}/ "  # trim trailing s for compactness
  done
  [[ -z "$res" ]] && res="-"

  # Pull the description: prefer YAML `description:` (handles quoted or bare, single line);
  # fall back to "(no frontmatter)" so broken skills surface.
  desc="$(awk '
    /^description:[[:space:]]/ {
      sub(/^description:[[:space:]]*/, "")
      gsub(/^"/, ""); gsub(/"[[:space:]]*$/, "")
      print; exit
    }
  ' "$skill")"

  if [[ -z "$desc" ]]; then
    if ! head -1 "$skill" | grep -q '^---'; then
      desc="(no YAML frontmatter — broken)"
    else
      desc="(no description field)"
    fi
  fi

  # Trim to ~40 words.
  desc="$(printf '%s' "$desc" | tr '\n' ' ' | awk '{ for(i=1;i<=NF && i<=40;i++) printf "%s ", $i; if (NF>40) printf "…" }')"

  printf '%-22s | %5s | %-18s | %s\n' "$name" "$lines" "$res" "$desc"
done
