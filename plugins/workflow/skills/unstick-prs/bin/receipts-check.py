#!/usr/bin/env python3
"""receipts-check.py — the gate before flipping a PR ready.

    gh pr checks <n> --json name,state,bucket | python3 receipts-check.py --body BODY_FILE
    (or: --checks FILE instead of stdin; --body - to read the body from stdin too, in which
    case pass --checks as a file)

LIVE, deterministic part (a script beats a model here — this is exactly the bug that shipped):
reads the named check contexts (`gh pr checks ... --json name,state,bucket`, JSON array or the
plain-text table form both work) and exits 1 if there are ZERO of them — "empty rollup is not
green" was a real sweep's bug (two PRs flipped ready on a repo with no CI at all, backed only
by self-tests). Exits 0 when at least one named check exists; this gate
does not itself judge whether those checks are green — the skill's existing "checks green or
failure documented" rule still does that.

Optional shadow judge part (log only, never gates; skipped when JUDGE_CMD is unset): batches
ONE question against the PR body — does its
verification section show a check that actually executed and passed, or only a claim? Logged
to site "unstick-prs:receipts". Runs best-effort regardless of the deterministic result, so the
log accumulates evidence on both green and red rollups; a failure here never changes the exit
code and never blocks anything beyond what the deterministic check already decided.

Exit: 0  at least one named check context exists (the deterministic gate passes)
      1  zero named check contexts — refuse to consider this rollup green
      2  usage error

Env: JUDGE_CMD     command that reads {"state", "questions": [{"id", "type": "yes_no",
                   "question"}]} on stdin and prints {"verdicts": [{"id", "answer": 0.0-1.0,
                   "escalate": bool}], "latencyMs"?, "usage"?}. No default: unset skips the
                   shadow part entirely.
     JUDGE_REDACT  redactor filter, text in -> text out (no default: unset or missing means
                   nothing is sent)
     JUDGE_LOG     override the shadow log path (default ~/.local/state/unstick-prs/receipts.jsonl)
"""
import json
import os
import re
import shlex
import subprocess
import sys
import time

MAX_BODY = 6000
MAX_CHECKS = 100
DEFAULT_JUDGE = ""    # no default judge: unset skips the shadow part
DEFAULT_REDACT = ""   # no default redactor: unset means nothing is sent
DEFAULT_LOG = os.path.expanduser("~/.local/state/unstick-prs/receipts.jsonl")
SITE = "unstick-prs:receipts"


def parse_args(argv):
    args = {"checks": None, "body": None, "pr": None}
    it = iter(argv)
    for a in it:
        key = {"--checks": "checks", "--body": "body", "--pr": "pr"}.get(a)
        if not key:
            raise SystemExit(f"unknown arg {a}")
        args[key] = next(it, None)
    return args


def read_source(path):
    """path is a file path, '-' for stdin, or None (also stdin)."""
    if path in (None, "-"):
        return sys.stdin.read()
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_checks(text):
    """Accepts `gh pr checks --json name,state,bucket` JSON, or the plain-text table
    `gh pr checks` prints without --json. Either way, returns one dict per named check."""
    text = (text or "").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except ValueError:
        pass
    rows = []
    for line in text.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        parts = re.split(r"\t+", line) if "\t" in line else re.split(r"\s{2,}", line)
        name = (parts[0] if parts else line).strip()
        if not name:
            continue
        rows.append({"name": name, "raw": line.strip()})
    return rows


def build_state(checks, body):
    return json.dumps({
        "n_checks": len(checks),
        "checks": checks[:MAX_CHECKS],
        "pr_body": (body or "")[:MAX_BODY],
    }, indent=1)


def questions():
    return [{"id": "receipts", "type": "yes_no",
             "question": "Does the PR body's verification section show a check that "
                         "actually executed and passed (not just a claim that it did)?"}]


def redact(text, redactor):
    if not os.path.isfile(redactor):
        return None, f"redactor missing at {redactor}; nothing sent"
    r = subprocess.run([sys.executable, redactor], input=text, capture_output=True, text=True)
    if r.returncode != 0:
        return None, f"redactor refused (exit {r.returncode})"
    return r.stdout, None


def call_judge(request, judge_cmd):
    try:
        r = subprocess.run(shlex.split(judge_cmd), input=json.dumps(request), capture_output=True,
                           text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"judge call failed: {e}"
    if r.returncode not in (0, 3):
        return None, f"judge exit {r.returncode}: {r.stderr.strip()[:200]}"
    try:
        out = json.loads(r.stdout)
    except ValueError:
        return None, "judge returned non-JSON"
    if any(v.get("hint") == "unreachable" or v.get("reason") == "unreachable"
           for v in out.get("verdicts", [])):
        return None, "judge unreachable"
    return out, None


def append_log(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def shadow_verdict(checks, body, pr, log_path):
    """Best-effort, log-only. Never raises past main(), never affects the exit code."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    judge_cmd = os.environ.get("JUDGE_CMD", DEFAULT_JUDGE)
    if body is None or not judge_cmd:
        return
    state, err = redact(build_state(checks, body), os.environ.get("JUDGE_REDACT", DEFAULT_REDACT))
    judge = None
    t0 = time.time()
    if not err:
        req = {"state": state, "questions": questions()}
        judge, err = call_judge(req, judge_cmd)
    if err:
        if log_path:
            append_log(log_path, {"ts": ts, "site": SITE, "mode": "shadow", "pr": pr, "error": err})
        return
    verdicts = {v["id"]: v for v in judge.get("verdicts", [])}
    row = {"ts": ts, "site": SITE, "mode": "shadow", "pr": pr,
           "n_questions": len(verdicts), "latencyMs": judge.get("latencyMs"),
           "usage": judge.get("usage"),
           "answers": {vid: v.get("answer") for vid, v in verdicts.items()},
           "escalated": [vid for vid, v in verdicts.items() if v.get("escalate")],
           "wall_s": round(time.time() - t0, 2)}
    if log_path:
        append_log(log_path, row)
    print(json.dumps(row))


def main(argv):
    try:
        args = parse_args(argv)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2

    checks = parse_checks(read_source(args["checks"]))
    body = read_source(args["body"]) if args["body"] else None

    try:
        shadow_verdict(checks, body, args["pr"], os.environ.get("JUDGE_LOG", DEFAULT_LOG))
    except Exception as e:  # shadow half is never allowed to affect the live gate
        print(f"receipts-check: shadow verdict non-fatal error: {e}", file=sys.stderr)

    if not checks:
        print("receipts-check: 0 named check contexts — empty rollup is not green",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
