#!/usr/bin/env python3
"""wrap_verdict.py — compute the session's status word from evidence, not from the agent.

    wrap_evidence.py <transcript> | wrap_verdict.py [--report FILE] [--log FILE|--no-log]

Reads wrap_evidence.py JSON on stdin. A judge model (optional, see JUDGE_CMD) answers typed questions about each of the user's
asks; code (combine(), below) turns the verdicts into DONE / PARTIAL / BLOCKED. The agent's
claimed status is parsed from the first line of its report (--report FILE, else the
evidence's last assistant message) and compared.

Exit: 0 claim is no better than computed
      1 claim is better than computed, or the report has no status word
      2 usage / bad input, or the state holds a key-shaped string (refused: nothing is sent),
        or the judge's reply lacks a well-formed verdict for some question asked (nothing judged;
        stderr carries one "wrap_verdict: bad-verdicts missing=… malformed=…" line)
      3 advisory: no judge configured, the judge unreachable, or the configured redactor
        refused — nothing downgraded
        (fail open on availability; a secret never leaves: key shapes are refused, not sent)

The judge only ever DOWNGRADES. It can move a claim from DONE to PARTIAL/BLOCKED; nothing here can
upgrade a claim or authorize anything.

Env: JUDGE_CMD    command that reads a request on stdin and prints JSON on stdout. No default:
                  unset means no judge, and the run is advisory (exit 3). Request:
                    {"state": "<JSON string>", "questions": [
                      {"id", "type": "yes_no", "question"}                  answer: 0.0-1.0
                      {"id", "type": "choice", "question", "options": {..}} answer: an option key
                      {"id", "type": "score",  "question", "levels": [..]}  answer: a level index]}
                  Response: {"verdicts": [{"id", "answer", "escalate": bool, "confidence"?}],
                             "model"?, "latencyMs"?, "usage"?}
                  Exit 0, or 3 when some verdict escalated; a verdict whose reason/hint is
                  "unreachable" means the judge was down.
     JUDGE_REDACT   OPTIONAL redactor filter (a Python script, text in -> text out). Unset,
                  empty or missing on disk: the state is sent unredacted (key shapes are still
                  refused) and the row says redacted:false — set one if the judge is a
                  third-party service. Set and present: it runs, fail-closed — if it refuses,
                  nothing is sent (exit 3).
"""
import json
import os
import re
import shlex
import subprocess
import sys
import time

RANK = {"DONE": 3, "UNCLEAR": 3, "n/a": 3, "PARTIAL": 2, "BLOCKED": 2, "FAILED": 1}
GAP_STATES = {"partial", "not-started", "narrowed", "delivered-unverified"}
CLAIMS = {"DONE": "says the work is finished", "PARTIAL": "says some of it remains",
          "BLOCKED": "says it is waiting on someone or something",
          "FAILED": "says it could not be done", "none": "makes no completion claim"}
COMPLETENESS = ["nothing asked for was delivered", "a small fraction was delivered",
                "most was delivered, with real gaps", "all delivered, but unverified or with a "
                "step left for the user", "all delivered and verified, nothing left for the user"]
STATES = {
    "delivered-verified": "done, and the report names a check that ran and passed, or the "
                          "evidence shows it (a merged PR, green named checks)",
    "delivered-unverified": "claimed done, but no named test, check, or evidence shows it works",
    "partial": "some of what was asked was done and some was not",
    "not-started": "nothing in the evidence or report addresses it",
    "narrowed": "a smaller or different version of the ask was delivered than what was asked",
}
MAX_ASKS = 20
MAX_REPORT = 6000
MAX_FILES = 60
DEFAULT_JUDGE = ""   # no default judge: unset means advisory exit 3
DEFAULT_LOG = os.path.expanduser("~/.local/state/wrap/verdicts.jsonl")

# Credential shapes. If one survives into the state that would be
# sent, the whole call is refused — exit 2, nothing sent. Left-anchored so "risk-assessment-…"
# is not read as an sk- key.
_B = r"(?<![A-Za-z0-9_])"
KEY_SHAPES = [
    ("private-key block", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("OpenRouter/Anthropic key", _B + r"sk-(?:or-v1-|ant-)[A-Za-z0-9_\-]{20,}"),
    ("OpenAI-style key", _B + r"sk-(?:proj-)?[A-Za-z0-9_\-]{32,}"),
    ("Stripe key", _B + r"[sr]k_live_[A-Za-z0-9]{20,}"),
    ("GitHub token", _B + r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})"),
    ("Slack token", _B + r"xox[abposr]-[A-Za-z0-9\-]{10,}"),
    ("AWS access key id", _B + r"AKIA[0-9A-Z]{16}(?![A-Za-z0-9])"),
    ("Google API key", _B + r"AIza[0-9A-Za-z_\-]{35}"),
    ("1Password service-account token", _B + r"ops_eyJ[A-Za-z0-9_\-]{20,}"),
    ("JWT", _B + r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
]
KEY_RES = [(name, re.compile(rx)) for name, rx in KEY_SHAPES]

CLAIM_RE = re.compile(r"^\W*(DONE|PARTIAL|BLOCKED|FAILED)\b")
LEGACY = [(re.compile(r"^\W*(still going|almost done)\b", re.I), "PARTIAL"),
          (re.compile(r"^\W*(done|complete|completed|shipped)\b", re.I), "DONE")]


def claimed_status(report):
    first = next((ln for ln in (report or "").splitlines() if ln.strip()), "")
    m = CLAIM_RE.match(first)
    if m:
        return m.group(1)
    for rx, word in LEGACY:
        if rx.match(first):
            return word
    return "none"


def build_state(ev, report):
    repos = []
    for r in ev.get("repos", []):
        pr = r.get("pr") or {}
        repos.append({
            "repo": os.path.basename(r.get("path", "")), "branch": r.get("branch"),
            "branch_state": r.get("branch_state"),
            "commits_ahead_of_default": (r.get("vs_default") or {}).get("ahead"),
            "dirty_files_in_checkout": r.get("dirty_files"),
            "pr": {k: pr.get(k) for k in ("number", "state", "draft", "named_checks")} if pr else None,
        })
    home = os.path.expanduser("~")
    written = [p.replace(home, "~") for p in ev.get("write_paths", [])][:MAX_FILES]
    return json.dumps({
        "users_messages": [{"n": a["i"], "kind": a["channel"], "text": a["text"]}
                             for a in ev["asks"]],
        "git_evidence": repos,
        "files_written_this_session": written,
        "agents_final_report": (report or "")[:MAX_REPORT],
    }, indent=1)


def questions(asks):
    qs = []
    for a in asks:
        if a["channel"] == "decision":
            continue  # their answers to questions are constraints, not deliverables
        n = a["i"]
        qs.append({"id": f"req_{n}", "type": "yes_no",
                   "question": f"Is the user's message #{n} a request for work or a deliverable "
                               "(not only an approval, an acknowledgement, or an answer)?"})
        qs.append({"id": f"sup_{n}", "type": "yes_no",
                   "question": f"Did a LATER message from the user replace or fold in message #{n}, "
                               "so it no longer needs delivering on its own?"})
        qs.append({"id": f"state_{n}", "type": "choice",
                   "question": f"Judged only from git_evidence and the agent's final report, how far "
                               f"did the session get on the user's message #{n}?",
                   "options": STATES})
    qs.append({"id": "unverified_claim", "type": "yes_no",
               "question": "Does the agent's final report claim a test, check, or verification "
                           "that neither the report's own output nor git_evidence shows was run?"})
    qs.append({"id": "lands_on_user", "type": "yes_no",
               "question": "Does the report leave a step the user must take before the work they asked "
                           "for is complete or usable (run something, approve, merge, send, decide)? "
                           "An optional look at finished work does not count."})
    qs.append({"id": "claimed_j", "type": "choice",
               "question": "In effect, what completion status does the agent's final report claim?",
               "options": CLAIMS})
    qs.append({"id": "completeness", "type": "score",
               "question": "Across everything the user asked for, how completely did the session "
                           "deliver it, by a strict standard: verified, nothing narrowed, nothing "
                           "left for them?",
               "levels": COMPLETENESS})
    return qs


def combine(asks, verdicts, claimed):
    """Pure. verdicts: {id: verdict}. Returns the verdict object (no I/O).

    Downgrades fire only on CONFIDENT gaps (escalate false). An escalated verdict is listed
    under `unsure` for a human to look at and never moves the status: a gate that fires on
    every doubt fires on everything, and gets ignored (a first trial, 2026-09-28: 5/5 sessions
    PARTIAL, including a control the user had scored 4 of 5).
    """
    def conf(vid):
        v = verdicts.get(vid)
        return bool(v) and not v.get("escalate")

    def p(vid, default=0.0):
        v = verdicts.get(vid)
        return v.get("answer", default) if v and isinstance(v.get("answer"), (int, float)) else default

    per, reasons, unsure = [], [], []
    for a in asks:
        if a["channel"] == "decision":
            continue
        n = a["i"]
        rv, st = verdicts.get(f"req_{n}"), verdicts.get(f"state_{n}")
        is_req = p(f"req_{n}") >= 0.5 or bool(rv and rv.get("escalate") and p(f"req_{n}") >= 0.3)
        superseded = p(f"sup_{n}") >= 0.5 and conf(f"sup_{n}")
        state = st.get("answer") if st else None
        sure = conf(f"state_{n}")
        per.append({"n": n, "text": a["text"][:140], "request": is_req, "superseded": superseded,
                    "state": state, "sure": sure, "confidence": (st or {}).get("confidence")})
    active = [x for x in per if x["request"] and not x["superseded"]]
    unverified = p("unverified_claim") >= 0.5 and conf("unverified_claim")
    lands = p("lands_on_user") >= 0.5 and conf("lands_on_user")
    for vid in ("unverified_claim", "lands_on_user"):
        if verdicts.get(vid) and not conf(vid):
            unsure.append(vid)

    claimed_source = "first-line"
    if claimed == "none" and conf("claimed_j") and verdicts["claimed_j"].get("answer") in RANK:
        claimed, claimed_source = verdicts["claimed_j"]["answer"], "judge-read"

    gaps = [x for x in active if x["sure"] and x["state"] in GAP_STATES]
    unsure += [f"#{x['n']}" for x in active if not x["sure"]]
    for x in gaps:
        reasons.append(f"#{x['n']} {x['state']}")
    if unverified:
        reasons.append("report claims a verification the evidence does not show")
    if lands:
        reasons.append("a remaining step lands on the user")
    if not active:
        computed = "n/a"
        reasons.append("no active request found in the user's messages")
    elif gaps or unverified:
        computed = "PARTIAL"
    elif lands:
        computed = "BLOCKED"
    elif all(x["sure"] and x["state"] == "delivered-verified" for x in active):
        computed = "DONE"
    else:
        computed = "UNCLEAR"   # no confident gap, not confidently done: passes, flagged
    consistent = claimed != "none" and RANK.get(claimed, 0) <= RANK[computed]
    if claimed == "none":
        reasons.append("report carries no status claim (DONE/PARTIAL/BLOCKED/FAILED)")
    comp = verdicts.get("completeness") or {}
    return {"computed": computed, "claimed": claimed, "claimed_source": claimed_source,
            "consistent": consistent, "reasons": reasons, "unsure": unsure,
            "completeness": comp.get("answer") if isinstance(comp.get("answer"), (int, float)) else None,
            "asks": per, "flags": {"unverified_claim": unverified, "lands_on_user": lands}}


def call_judge(request, judge_cmd):
    if not judge_cmd:
        return None, "no judge configured (JUDGE_CMD unset)"
    try:
        r = subprocess.run(shlex.split(judge_cmd), input=json.dumps(request), capture_output=True,
                           text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"judge call failed: {e}"
    # 0 = all confident, 3 = some verdict escalated (output still valid), anything else = error
    if r.returncode not in (0, 3):
        return None, f"judge exit {r.returncode}: {r.stderr.strip()[:200]}"
    try:
        out = json.loads(r.stdout)
    except ValueError:
        return None, "judge returned non-JSON"
    vs = out.get("verdicts") if isinstance(out, dict) else None
    if isinstance(vs, list) and any(
            isinstance(v, dict) and (v.get("hint") == "unreachable" or v.get("reason") == "unreachable")
            for v in vs):
        return None, "judge unreachable"
    return out, None


def redact(text, redactor):
    if not os.path.isfile(redactor):
        return None, f"redactor missing at {redactor}; nothing sent"
    r = subprocess.run([sys.executable, redactor], input=text, capture_output=True, text=True)
    if r.returncode != 0:
        return None, f"redactor refused (exit {r.returncode})"
    return r.stdout, None


def key_shape(text):
    """Name of the first credential shape found in text, else None. Never returns the match."""
    return next((name for name, rx in KEY_RES if rx.search(text)), None)


def _well_typed(q, answer):
    if q["type"] == "yes_no":
        return isinstance(answer, (int, float)) and not isinstance(answer, bool) and 0 <= answer <= 1
    if q["type"] == "choice":
        return isinstance(answer, str) and answer in q["options"]
    if q["type"] == "score":
        return (isinstance(answer, (int, float)) and not isinstance(answer, bool)
                and 0 <= answer <= len(q["levels"]) - 1)
    return False


def bad_verdicts(qs, judge):
    """(missing_ids, malformed_ids) for the questions asked, in question order.

    Runs BEFORE combine(): a reply that leaves questions out must not read as "nothing to
    judge" (combine() maps no active request to n/a, which ranks with DONE). Well-formed means
    a dict with the question's id and a bool `escalate`; a confident verdict carries an answer
    of the question's type; an escalated one may carry null (it never reached the judge).
    """
    vs = judge.get("verdicts") if isinstance(judge, dict) else None
    by_id = {}
    for v in vs if isinstance(vs, list) else []:
        if isinstance(v, dict) and isinstance(v.get("id"), str):
            by_id.setdefault(v["id"], v)
    missing, malformed = [], []
    for q in qs:
        v = by_id.get(q["id"])
        if v is None:
            missing.append(q["id"])
        elif not isinstance(v.get("escalate"), bool):
            malformed.append(q["id"])
        elif v.get("answer") is None and v["escalate"]:
            continue
        elif not _well_typed(q, v.get("answer")):
            malformed.append(q["id"])
    return missing, malformed


def _ids(ids, total):
    if len(ids) == total:
        return f"all({total})"
    return ",".join(ids[:20]) + (f",+{len(ids) - 20}" if len(ids) > 20 else "")


def append_log(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def main(argv):
    report_file, log = None, DEFAULT_LOG
    it = iter(argv)
    for a in it:
        if a == "--report":
            report_file = next(it, None)
        elif a == "--log":
            log = next(it, None)
        elif a == "--no-log":
            log = None
        else:
            print(f"unknown arg {a}", file=sys.stderr)
            return 2
    try:
        ev = json.load(sys.stdin)
        asks = ev["asks"][-MAX_ASKS:]
    except (ValueError, KeyError, TypeError):
        print("stdin must be wrap_evidence.py JSON", file=sys.stderr)
        return 2
    report = open(report_file, encoding="utf-8").read() if report_file else ev.get("report")
    claimed = claimed_status(report)
    ev = dict(ev, asks=asks)

    state, err, redacted = build_state(ev, report), None, False
    redactor = os.environ.get("JUDGE_REDACT") or ""
    if redactor and os.path.isfile(redactor):
        state, err = redact(state, redactor)
        redacted = err is None
    elif redactor:
        print(f"JUDGE_REDACT={redactor} does not exist; sending the state unredacted",
              file=sys.stderr)
    if not err:
        kind = key_shape(state)
        if kind:
            print(f"state holds a key-shaped string ({kind}); refusing to send it to the judge. "
                  "Nothing was sent.", file=sys.stderr)
            return 2
    judge = None
    if not err:
        qs = questions(asks)
        req = {"state": state, "questions": qs}
        t0 = time.time()
        judge, err = call_judge(req, os.environ.get("JUDGE_CMD", DEFAULT_JUDGE))
    if err:
        out = {"computed": None, "claimed": claimed, "consistent": None, "advisory": err,
               "session_id": ev.get("session_id")}
        json.dump(out, sys.stdout, indent=1)
        sys.stdout.write("\n")
        return 3
    missing, malformed = bad_verdicts(qs, judge)
    if missing or malformed:
        parts = ([f"missing={_ids(missing, len(qs))}"] if missing else []) + \
                ([f"malformed={_ids(malformed, len(qs))}"] if malformed else [])
        print(f"wrap_verdict: bad-verdicts {' '.join(parts)}", file=sys.stderr)
        print(f"The judge's reply lacks a well-formed verdict for {len(missing) + len(malformed)} of "
              f"{len(qs)} questions; nothing judged.", file=sys.stderr)
        return 2
    verdicts = {v["id"]: v for v in judge["verdicts"] if isinstance(v, dict) and "id" in v}
    out = combine(asks, verdicts, claimed)
    out["session_id"] = ev.get("session_id")
    out["judge"] = {k: judge.get(k) for k in ("model", "latencyMs", "usage")}
    out["redacted"] = redacted
    if log:
        append_log(log, {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                         "site": "wrap:verdict", "mode": "shadow",
                         "session": ev.get("session_id"), "computed": out["computed"],
                         "claimed": claimed, "n_questions": len(verdicts),
                         "redacted": redacted,
                         "latencyMs": out["judge"]["latencyMs"], "usage": out["judge"]["usage"],
                         "wall_s": round(time.time() - t0, 2)})
    json.dump(out, sys.stdout, indent=1)
    sys.stdout.write("\n")
    return 0 if out["consistent"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
