#!/usr/bin/env python3
"""overlap-judge.py — optional second-model overlap check for learn Mode B, hygiene-heuristics
check 1 ("Overlap / MECE violation"). LOG-ONLY: writes one line to a log and prints a summary;
never opens an issue, never edits a skill. Meant as a non-fatal extra step in a scheduled
skill-hygiene run — any failure here must never change that run's exit code.

Takes `scripts/scan-skills.sh`'s table on stdin, builds candidate pairs deterministically:
skills whose descriptions share "distinctive" words — tokens that are NOT common across the
whole inventory, so generic instructive verbs ("use", "audit", "skill"...) don't pair every
skill with every other one. Bounded to <=40 pairs (highest shared-token count first), then
asks a judge model, in ONE batch: "Do these two skills compete for the same trigger phrases?"

Usage:
  scripts/scan-skills.sh | scripts/overlap-judge.py

Env:
  JUDGE_CMD     command that reads a request on stdin and prints JSON on stdout. No default:
                unset means the check is skipped. Request:
                  {"state": "<redacted JSON of the skills involved>",
                   "questions": [{"id": "pair_0", "type": "yes_no", "question": "..."}]}
                Response:
                  {"verdicts": [{"id": "pair_0", "answer": 0.0-1.0, "escalate": false}],
                   "latencyMs": <optional>, "usage": <optional>}
                Exit 0 (or 3, "some escalated") is success; a verdict whose reason/hint is
                "unreachable" means the judge was down.
  JUDGE_REDACT  redactor filter (a Python script), text in -> redacted text out. No default:
                unset or missing means nothing is sent (fail closed on privacy).
  JUDGE_LOG     log path (default: ~/.local/state/learn/overlap.jsonl)

Always exits 0 (fail-open by design — see main()); the only way to see a problem is the
printed message or the log.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import time
from itertools import combinations

SITE = "learn:overlap"
DEFAULT_JUDGE = ""   # no default judge: unset means skip
DEFAULT_REDACT = ""   # no default redactor: unset means nothing is sent
DEFAULT_LOG = os.path.expanduser("~/.local/state/learn/overlap.jsonl")
MAX_PAIRS = 40
MIN_SHARED = 2      # a pair needs at least this many distinctive shared tokens to qualify
MAX_DOC_FREQ = 5     # a token shared by more skills than this isn't "distinctive" — noise

STOPWORDS = {
    "this", "that", "these", "those", "with", "from", "into", "also", "only", "never",
    "always", "before", "after", "same", "which", "what", "does", "used", "using", "uses",
    "your", "their", "across", "some", "each", "every", "skill", "skills", "trigger",
    "triggers", "phrase", "phrases", "description", "use", "the", "and", "for", "not",
    "name", "names", "says", "user", "audit", "audits", "build", "builds", "building",
    "new", "user", "users", "agent", "agents", "session", "sessions", "when", "asks",
    "asked", "make", "makes", "making", "work", "works", "working", "step", "steps",
    "then", "than", "have", "has", "had", "will", "would", "should", "could", "about",
    "over", "under", "such", "like", "here", "there", "where", "while", "shows", "show",
    "give", "gives", "given", "one", "two", "three", "any", "all", "both", "own", "own",
}
TOKEN_RE = re.compile(r"[a-z][a-z0-9\-]{3,}")


def parse_rows(text):
    """scan-skills.sh emits `NAME | LINES | RESOURCES | DESCRIPTION` rows."""
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("---"):
            continue
        parts = line.split(" | ")
        if len(parts) != 4:
            continue
        name = parts[0].strip()
        if name == "NAME":
            continue
        desc = parts[3].strip()
        if desc.startswith("(no SKILL.md)") or "not a triggerable skill" in desc:
            continue
        rows.append({"name": name, "description": desc})
    return rows


def tokenize(desc):
    return {t for t in TOKEN_RE.findall(desc.lower()) if t not in STOPWORDS}


def candidate_pairs(rows):
    """Deterministic: shared *distinctive* tokens (doc-frequency <= MAX_DOC_FREQ) only,
    highest-shared-count first, capped at MAX_PAIRS."""
    toks = {r["name"]: tokenize(r["description"]) for r in rows}
    doc_freq = {}
    for s in toks.values():
        for t in s:
            doc_freq[t] = doc_freq.get(t, 0) + 1
    distinctive = {n: {t for t in s if doc_freq[t] <= MAX_DOC_FREQ} for n, s in toks.items()}

    scored = []
    names = [r["name"] for r in rows]
    for a, b in combinations(names, 2):
        shared = distinctive[a] & distinctive[b]
        if len(shared) >= MIN_SHARED:
            scored.append((len(shared), a, b, sorted(shared)))
    scored.sort(key=lambda x: (-x[0], x[1], x[2]))
    return scored[:MAX_PAIRS]


def build_state(rows, pairs):
    by_name = {r["name"]: r["description"] for r in rows}
    names = sorted({n for _, a, b, _ in pairs for n in (a, b)})
    return json.dumps({"skills": {n: by_name[n] for n in names}}, indent=1)


def build_questions(pairs):
    """One yes/no question per pair. The shared-word hint goes in the question text, not in a
    separate criteria field — some judge protocols treat free-text criteria as open-ended and
    escalate every question before the model runs."""
    qs = []
    for i, (score, a, b, shared) in enumerate(pairs):
        qs.append({
            "id": f"pair_{i}", "type": "yes_no",
            "question": (f"Do the skills '{a}' and '{b}' compete for the same trigger "
                        f"phrases? Shared distinctive words in their descriptions: "
                        f"{', '.join(shared)}."),
        })
    return qs


def redact(text, redactor):
    if not redactor or not os.path.isfile(redactor):
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


def main(argv, stdin_text=None, judge_cmd=None, redactor=None, log_path=None):
    text = stdin_text if stdin_text is not None else sys.stdin.read()
    judge_cmd = judge_cmd or os.environ.get("JUDGE_CMD", DEFAULT_JUDGE)
    redactor = redactor if redactor is not None else os.environ.get("JUDGE_REDACT", DEFAULT_REDACT)
    log_path = log_path if log_path is not None else os.environ.get("JUDGE_LOG", DEFAULT_LOG)
    if not judge_cmd:
        print("overlap-judge: JUDGE_CMD unset; skipping (optional check)")
        return 0

    rows = parse_rows(text)
    pairs = candidate_pairs(rows)
    if not pairs:
        print("overlap-judge: no candidate pairs (nothing shares a distinctive trigger word)")
        return 0

    state, err = redact(build_state(rows, pairs), redactor)
    if err:
        print(f"overlap-judge: {err}; skipping (fail closed on privacy)")
        return 0

    verdict, err = call_judge({"state": state, "questions": build_questions(pairs)}, judge_cmd)
    if err:
        print(f"overlap-judge: {err} (advisory only, continuing)")
        return 0

    verdicts = {v["id"]: v for v in verdict.get("verdicts", [])}
    flagged = [pairs[int(vid.split("_")[1])] for vid, v in verdicts.items()
              if isinstance(v.get("answer"), (int, float)) and v["answer"] >= 0.5
              and not v.get("escalate")]
    escalated = [vid for vid, v in verdicts.items() if v.get("escalate")]

    print(f"overlap-judge: {len(pairs)} candidate pairs, {len(flagged)} flagged as overlapping, "
         f"{len(escalated)} escalated (shadow, log-only)")
    for score, a, b, shared in flagged:
        print(f"  [overlap?] {a} <-> {b}  shared={','.join(shared)}")

    try:
        append_log(log_path, {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "site": SITE,
            "mode": "shadow", "n_questions": len(pairs), "latencyMs": verdict.get("latencyMs"),
            "usage": verdict.get("usage"),
            "answers": {vid: v.get("answer") for vid, v in verdicts.items()},
            "escalated": escalated,
        })
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
