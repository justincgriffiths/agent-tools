#!/usr/bin/env bash
# wrap_status.sh — wrap-status: compute this session's status word and keep the verdict.
# The thin wrapper that owns the side effects, so wrap_evidence.py and wrap_verdict.py stay
# filters. It finds the transcript, runs the pipeline, saves the verdict and logs the run.
#
#   wrap_status.sh [--transcript PATH] <draft-report-file>
#
#   transcript  --transcript PATH, else the ONE match of
#               $WRAP_PROJECTS_DIR/*/$CLAUDE_CODE_SESSION_ID.jsonl (zero or several: exit 2)
#   pipeline    wrap_evidence.py <transcript> | wrap_verdict.py --report <draft>
#               [--log "$WRAP_VERDICT_LOG"], with pipefail
#   verdict     printed on stdout; on exit 0/1/3 the same bytes are saved to
#               $WRAP_STATE_DIR/<session_id>.json (umask 077: file 0600, dir 0700). The
#               session_id comes from the verdict JSON, falling back to $CLAUDE_CODE_SESSION_ID
#   log         one line per run appended to $WRAP_STATE_DIR/wrap_status.log
#
# Exit = wrap_verdict.py's: 0 consistent · 1 overclaim or no status word · 3 advisory (no judge
#   configured or the judge unavailable, nothing downgraded) · 2 bad input: no or ambiguous
#   transcript, missing draft, wrap_evidence failed, wrap_verdict refused, or its stdout was not verdict JSON. A Python
#   crash exits 1 with a traceback, and that is not an overclaim. Nor is a judge reply missing
#   verdicts: wrap_verdict exits 2 and the log line gets its "missing=… malformed=…" ids.
#   Exit 2 saves no file.
#
# Env: CLAUDE_CODE_SESSION_ID  set by the harness in Bash; picks the transcript
#      WRAP_PROJECTS_DIR       transcript root (default ~/.claude/projects)
#      WRAP_STATE_DIR          verdict files and the log (default ~/.local/state/wrap)
#      WRAP_VERDICT_LOG        passed to wrap_verdict.py as --log (unset: its own shadow log)
#      WRAP_PYTHON             interpreter (default python3)
#      JUDGE_CMD, JUDGE_REDACT read by wrap_verdict.py (no JUDGE_CMD: advisory exit 3)
set -uo pipefail   # no -e: the pipeline's exit code IS the verdict, so it is captured, not fatal
umask 077
# lowercase on purpose: an UPPERCASE name here would overwrite an inherited, exported variable
# of the same name and leak into the python children (a test's STATE did exactly that)

bin_dir="$(cd "$(dirname "$0")" && pwd)"
state_dir="${WRAP_STATE_DIR:-$HOME/.local/state/wrap}"
projects_dir="${WRAP_PROJECTS_DIR:-$HOME/.claude/projects}"
py="${WRAP_PYTHON:-python3}"
log="$state_dir/wrap_status.log"
argv="$*"
sid_re='^[A-Za-z0-9_-]+$'   # a session id is a filename part: no "/", no ".."
usage="usage: wrap_status.sh [--transcript PATH] <draft-report-file>"
computed=- claimed=- bad="" tmp="" errf=""
trap '[ -n "$tmp" ] && rm -f "$tmp"; [ -n "$errf" ] && rm -f "$errf"' EXIT

# the one way out: rc arrives as an argument, captured by the caller before any timestamp
finish() {
  local rc=$1
  if mkdir -p "$state_dir" 2>/dev/null; then
    printf '[%s] argv=[%s] exit=%s computed=%s claimed=%s%s\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$argv" "$rc" "$computed" "$claimed" "${bad:+ $bad}" >> "$log"
  else
    echo "wrap_status: cannot create $state_dir; this run is not logged" >&2
  fi
  exit "$rc"
}
fail() { echo "wrap_status: $1" >&2; finish 2; }

transcript="" draft=""
while [ $# -gt 0 ]; do
  case "$1" in
    --transcript) [ $# -ge 2 ] || fail "--transcript needs a path. $usage"
                  transcript="$2"; shift 2 ;;
    -*)           fail "unknown flag $1. $usage" ;;
    *)            [ -z "$draft" ] || fail "one draft report only. $usage"
                  draft="$1"; shift ;;
  esac
done
[ -n "$draft" ] || fail "$usage"
[ -f "$draft" ] && [ -r "$draft" ] || fail "draft report $draft is not a readable file"

if [ -z "$transcript" ]; then
  sid="${CLAUDE_CODE_SESSION_ID:-}"
  [ -n "$sid" ] || fail "CLAUDE_CODE_SESSION_ID is unset; pass --transcript PATH"
  [[ "$sid" =~ $sid_re ]] || fail "CLAUDE_CODE_SESSION_ID is not a session id; pass --transcript PATH"
  shopt -s nullglob
  matches=("$projects_dir"/*/"$sid".jsonl)
  shopt -u nullglob
  case ${#matches[@]} in
    1) transcript="${matches[0]}" ;;
    0) fail "no transcript for session $sid under $projects_dir; pass --transcript PATH" ;;
    *) fail "${#matches[@]} transcripts match session $sid under $projects_dir; pass --transcript PATH" ;;
  esac
fi
[ -f "$transcript" ] && [ -r "$transcript" ] || fail "transcript $transcript is not a readable file"

mkdir -p "$state_dir" || fail "cannot create $state_dir"
tmp="$(mktemp "$state_dir/.verdict.XXXXXX")" || fail "cannot create a temp file in $state_dir"
errf="$(mktemp "$state_dir/.stderr.XXXXXX")" || fail "cannot create a temp file in $state_dir"
vargs=(--report "$draft")
[ -n "${WRAP_VERDICT_LOG:-}" ] && vargs+=(--log "$WRAP_VERDICT_LOG")

# wrap_verdict's stderr goes via a file (replayed below) so the log can name bad verdict ids
"$py" "$bin_dir/wrap_evidence.py" "$transcript" \
  | "$py" "$bin_dir/wrap_verdict.py" "${vargs[@]}" > "$tmp" 2> "$errf"
ps=("${PIPESTATUS[@]}")
ev_rc=${ps[0]} rc=${ps[1]}
cat "$errf" >&2
bad="$(sed -n 's/^wrap_verdict: bad-verdicts //p' "$errf" | head -n 1)"

[ "$ev_rc" -eq 0 ] || fail "wrap_evidence.py failed (exit $ev_rc); no verdict"
case "$rc" in
  0|1|3) ;;
  2) fail "wrap_verdict.py exit 2 (bad input, a refusal, or missing verdicts); no verdict saved" ;;
  *) fail "wrap_verdict.py exit $rc; no verdict saved" ;;
esac

# session_id|computed|claimed from the verdict JSON; non-zero if stdout is not a verdict
parse='
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except (OSError, ValueError):
    sys.exit(1)
if not isinstance(d, dict) or "computed" not in d or "claimed" not in d:
    sys.exit(1)
w = lambda v: "null" if v is None else str(v).replace("|", "/").replace("\n", " ")
s = d.get("session_id")
print("|".join([s if isinstance(s, str) else "", w(d["computed"]), w(d["claimed"])]))
'
fields="$("$py" -c "$parse" "$tmp")"
json_rc=$?
if [ "$json_rc" -ne 0 ]; then
  cat "$tmp" >&2
  fail "wrap_verdict.py exit $rc but its stdout is not a verdict (a crash?); nothing saved"
fi
IFS='|' read -r j_sid computed claimed <<< "$fields"

out_sid="$j_sid"
[[ "$out_sid" =~ $sid_re ]] || out_sid="${CLAUDE_CODE_SESSION_ID:-}"
[[ "$out_sid" =~ $sid_re ]] || fail "no usable session id in the verdict or CLAUDE_CODE_SESSION_ID; nothing saved"
out="$state_dir/$out_sid.json"
mv -f "$tmp" "$out" || fail "cannot write $out"
tmp=""
cat "$out"
finish "$rc"
