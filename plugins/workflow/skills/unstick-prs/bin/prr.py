#!/usr/bin/env python3
"""prr.py — filter: ready-PR check rollups on stdin -> "ready but red" report on stdout.

Long name: list-ready-pull-requests-whose-ci-is-red

One job: decide whether any PR marked ready for review carries a failed or cancelled check
that is NOT also failing on its base branch. prd.py's sibling: prd answers "is anything
parked in draft?", prr answers "is anything ready that isn't green?".

INPUT (prr.sh builds it): a JSON list of
  {"repo": "o/r", "number": 1, "title": "...", "url": "...", "base": "staging",
   "checks": [<statusCheckRollup item>...], "base_red": ["audit", ...]}
statusCheckRollup items are CheckRun {name, status, conclusion} or StatusContext
{context, state}. base_red names the checks that are red on the base branch's head.

VERDICT per PR:
  red        a check failed/cancelled/timed out here and NOT on the base -> this PR's problem
  pending    a check has not finished -> not verified yet
  inherited  every red check is also red on the base (e.g. a repo-wide npm audit)
  no-ci      zero named checks (receipts-check.py treats this as not green; reported only)
  green      everything else

Exit code is the verdict (universal rule 2):
  0  no ready PR is red or pending
  1  one or more ready PRs are red
  3  input was not the JSON we expected — UNKNOWN, never read as clean
  4  none red, but one or more still pending — UNKNOWN until they finish

Why (2026-10-05): two PRs (an app repo and a routine library) were flipped ready at /wrap
while their checks had been CANCELLED by a GitHub runner outage. A draft check passed (no
drafts) and receipts-check.py passed (named checks existed); neither looks at conclusions. The user opened
their queue and found nothing actually ready to merge.
"""
import json
import sys

RED_CONCLUSIONS = {"FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE"}
RED_STATES = {"FAILURE", "ERROR"}
PENDING_STATES = {"PENDING", "EXPECTED"}


def norm(item):
    """(name, kind) where kind is red | pending | ok."""
    if "context" in item:                                    # StatusContext
        state = (item.get("state") or "").upper()
        kind = "red" if state in RED_STATES else "pending" if state in PENDING_STATES else "ok"
        return item["context"], kind
    name = item.get("name") or item.get("workflowName") or "?"
    if (item.get("status") or "").upper() != "COMPLETED":
        return name, "pending"
    return name, "red" if (item.get("conclusion") or "").upper() in RED_CONCLUSIONS else "ok"


def judge(pr):
    checks = [norm(c) for c in pr.get("checks") or []]
    if not checks:
        return "no-ci", []
    base_red = set(pr.get("base_red") or [])
    red = sorted({n for n, k in checks if k == "red"})
    own = [n for n in red if n not in base_red]
    if own:
        return "red", own
    if any(k == "pending" for _, k in checks):
        return "pending", sorted({n for n, k in checks if k == "pending"})
    if red:
        return "inherited", red
    return "green", []


try:
    rows = json.load(sys.stdin)
    if not isinstance(rows, list):
        raise ValueError("expected a list of PRs")
    verdicts = [(r, *judge(r)) for r in rows]
except Exception as e:                       # noqa: BLE001 - any malformed input is UNKNOWN
    print(f"UNKNOWN: could not parse ready-PR rollups ({e}).", file=sys.stderr)
    sys.exit(3)

for r, v, names in verdicts:
    detail = (" " + ",".join(names)) if names else ""
    print(f"{v:9}  {r['repo']}#{r['number']}  {r['title'][:60]}{detail}")

count = {v: sum(1 for _, x, _ in verdicts if x == v) for v in ("red", "pending", "inherited", "no-ci", "green")}
print(", ".join(f"{n} {v}" for v, n in count.items()) + f" / {len(rows)} ready", file=sys.stderr)
sys.exit(1 if count["red"] else 4 if count["pending"] else 0)
