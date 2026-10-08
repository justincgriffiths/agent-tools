#!/usr/bin/env bash
# hookrefs-selftest.sh — prove learn/scripts/hookrefs.sh catches dead hook citations.
#
# Builds a throwaway HOME (fake ~/.claude with settings.json + hooks) and a fake skill
# library, then checks:
#   clean tree (wired hook, placeholder, data file, nested reference)  -> exit 0, no output
#   planted ~/.claude/hooks/does-not-exist.sh + an unwired hook        -> exit 1, MISSING + UNWIRED
#   wired hook with the exec bit unset                                 -> NOT-EXEC
#   a cited name that is only a prefix of a wired one                  -> UNWIRED (token match)
#   no ~/.claude at all (CI runner)                                    -> exit 0, skip notice
#   missing library / unparseable settings.json                        -> exit 2
# Exit code is the verdict: 0 = all cases pass.
set -uo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts/hookrefs.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export HOME="$T/home" HOOKREFS_LOG="$T/hookrefs.log"
LIB="$T/lib"; H="$HOME/.claude/hooks"
mkdir -p "$H" "$LIB/alpha/references/deep" "$LIB/beta"

fail=0
check() { # $1=label $2=expected-exit $3=actual-exit [$4=extra condition result 0/1]
  if [ "$3" = "$2" ] && [ "${4:-0}" = 0 ]; then echo "PASS  $1"; else echo "FAIL  $1 (exit $3, want $2)"; fail=1; fi
}
run() { out="$(bash "$SRC" "$@" 2>"$T/err")"; rc=$?; }

printf '#!/bin/sh\n' >"$H/good.sh"; chmod +x "$H/good.sh"
printf '#!/bin/sh\n' >"$H/orphan.sh"; chmod +x "$H/orphan.sh"
printf '#!/bin/sh\n' >"$H/noexec.sh"
printf '#!/bin/sh\n' >"$H/copy-guard.sh"; chmod +x "$H/copy-guard.sh"
printf 'a\tb\n' >"$H/rules.tsv"
cat >"$HOME/.claude/settings.json" <<'JSON'
{ "hooks": {
    "Stop": [ { "hooks": [ { "type": "command", "command": "bash \"$HOME/.claude/hooks/good.sh\"" } ] } ],
    "PreToolUse": [ { "matcher": "Bash", "hooks": [
      { "type": "command", "command": "bash $HOME/.claude/hooks/noexec.sh" },
      { "type": "command", "command": "bash \"$HOME/.claude/hooks/copy-guard-bash.sh\"" } ] } ] } }
JSON

cat >"$LIB/alpha/SKILL.md" <<'MD'
---
name: alpha
---
Backstopped by `~/.claude/hooks/good.sh`, which reads `~/.claude/hooks/rules.tsv`.
Hooks live in `~/.claude/hooks/` and are wired in settings.json.

```bash
cp my-guard.sh ~/.claude/hooks/<name>.sh
```
MD
printf 'See $HOME/.claude/hooks/good.sh.\n' >"$LIB/alpha/references/deep/notes.md"

# 1. clean tree
run "$LIB"
check "clean tree exits 0 with no findings" 0 "$rc" "$([ -z "$out" ]; echo $?)"

# 2. planted missing + unwired
printf -- '---\nname: beta\n---\nEnforced by `~/.claude/hooks/does-not-exist.sh`.\nAlso ${HOME}/.claude/hooks/orphan.sh.\n' \
  >"$LIB/beta/SKILL.md"
run "$LIB"
check "planted missing + unwired exits 1" 1 "$rc"
grep -qx 'beta:SKILL.md:4 MISSING ~/.claude/hooks/does-not-exist.sh' <<<"$out"
check "  MISSING line names skill:file:line" 0 0 $?
grep -qx 'beta:SKILL.md:5 UNWIRED ~/.claude/hooks/orphan.sh' <<<"$out"
check "  UNWIRED line names skill:file:line" 0 0 $?
check "  exactly two findings" 0 0 "$([ "$(grep -c . <<<"$out")" = 2 ]; echo $?)"
rm "$LIB/beta/SKILL.md"

# 3. wired but not executable
printf -- '---\nname: beta\n---\nUses ~/.claude/hooks/noexec.sh\n' >"$LIB/beta/SKILL.md"
run "$LIB"
check "wired hook without exec bit is NOT-EXEC" 1 "$rc" \
  "$([ "$out" = 'beta:SKILL.md:4 NOT-EXEC ~/.claude/hooks/noexec.sh' ]; echo $?)"

# 4. prefix of a wired name is not wired
printf -- '---\nname: beta\n---\nUses ~/.claude/hooks/copy-guard.sh\n' >"$LIB/beta/SKILL.md"
run "$LIB"
check "copy-guard.sh is not wired by copy-guard-bash.sh" 1 "$rc" \
  "$([ "$out" = 'beta:SKILL.md:4 UNWIRED ~/.claude/hooks/copy-guard.sh' ]; echo $?)"
rm "$LIB/beta/SKILL.md"

# 5. unparseable settings -> 2
cp "$HOME/.claude/settings.json" "$T/settings.bak"
printf '{ not json' >"$HOME/.claude/settings.json"
run "$LIB"
check "unparseable settings.json exits 2" 2 "$rc"
cp "$T/settings.bak" "$HOME/.claude/settings.json"

# 6. missing library -> 2
run "$T/no-such-lib"
check "missing library exits 2" 2 "$rc"

# 7. no ~/.claude -> skip, 0
rm -rf "$HOME/.claude"
run "$LIB"
check "no ~/.claude skips with exit 0" 0 "$rc" "$(grep -q 'skip' "$T/err"; echo $?)"

# 8. every run logged its exit code
check "one log line per run, exit code recorded" 0 0 \
  "$([ "$(grep -c 'exit=' "$HOOKREFS_LOG")" = 7 ] && grep -q 'exit=1 ' "$HOOKREFS_LOG"; echo $?)"

exit $fail
