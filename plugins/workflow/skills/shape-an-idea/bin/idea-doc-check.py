#!/usr/bin/env python3
"""idea-doc-check — is a shape-an-idea doc finished?

Filter: reads the doc from the path argument (or stdin when the path is '-'), prints one
line per gap, and exits 1 on any gap, 0 when the doc is complete, 2 on a usage error.

  python3 bin/idea-doc-check.py docs/ideas/<slug>.md

Complete means:
  - all six sections are present, by heading
  - no section still says _pending_ (text inside HTML comments is ignored)
  - the decision log has at least one decision made by a person, not "agent (fact)"
  - Workflow v0 contains a table
  - Next moves holds at least one list item
"""
import re
import sys

SECTIONS = [
    "Problem statement",
    "Decision log",
    "Assumptions",
    "Research plan and findings",
    "Workflow v0",
    "Next moves",
]


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def split_sections(text: str) -> dict:
    out, current = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            current = m.group(1)
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def table_rows(body: str) -> list:
    rows = [l for l in body.splitlines() if l.strip().startswith("|")]
    # drop header + separator
    data = [r for r in rows[1:] if not re.match(r"^\|\s*:?-{2,}", r.strip())]
    return [[c.strip() for c in r.strip().strip("|").split("|")] for r in data]


def check(text: str) -> list:
    gaps = []
    sections = split_sections(strip_comments(text))
    for name in SECTIONS:
        if name not in sections:
            gaps.append(f"missing section: ## {name}")
        elif not sections[name] or "_pending_" in sections[name]:
            gaps.append(f"section still pending: ## {name}")

    log = sections.get("Decision log", "")
    human = [
        r for r in table_rows(log)
        if len(r) >= 4 and r[3] and "_pending_" not in r[1]
        and not r[3].lower().startswith("agent")
    ]
    if "Decision log" in sections and not human:
        gaps.append("decision log has no decision made by a person")

    wf = sections.get("Workflow v0", "")
    if "Workflow v0" in sections and not table_rows(wf):
        gaps.append("Workflow v0 has no step table")

    nm = sections.get("Next moves", "")
    if "Next moves" in sections and not re.search(r"^\s*(?:[-*]|\d+\.)\s+\S", nm, re.M):
        gaps.append("Next moves has no list items")
    return gaps


def main(argv: list) -> int:
    if len(argv) != 2:
        print("usage: idea-doc-check.py <doc.md | ->", file=sys.stderr)
        return 2
    try:
        text = sys.stdin.read() if argv[1] == "-" else open(argv[1], encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read {argv[1]}: {e}", file=sys.stderr)
        return 2
    gaps = check(text)
    for g in gaps:
        print(g)
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
