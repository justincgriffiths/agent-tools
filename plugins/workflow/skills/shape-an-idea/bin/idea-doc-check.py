#!/usr/bin/env python3
"""idea-doc-check — is a shape-an-idea doc finished?

Filter: reads the doc from the path argument (or stdin when the path is '-'), prints one
line per gap, and exits 1 on any gap, 0 when the doc is complete, 2 on a usage error.

  python3 bin/idea-doc-check.py docs/ideas/<slug>.md

Complete means:
  - all six sections are present, by heading
  - no section still says _pending_ (text inside HTML comments is ignored)
  - the decision log has at least one decision made by a person: its "Decided by" cell
    (found by header, not position) is not an agent and not marked "(fact)"
  - Workflow v0 contains a step table and an "N=1" run note
  - Next moves holds at least three list items
Headings match case-insensitively.
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
            current = m.group(1).lower()
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


SEP = re.compile(r"^\|(\s*:?-{2,}:?\s*\|)+\s*$")


def cells(line: str) -> list:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def tables(body: str) -> list:
    """Every markdown table in body as (header_cells, data_rows)."""
    lines = body.splitlines()
    out = []
    for i in range(1, len(lines)):
        if SEP.match(lines[i].strip()) and lines[i - 1].strip().startswith("|"):
            rows, j = [], i + 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(cells(lines[j]))
                j += 1
            out.append(([c.lower() for c in cells(lines[i - 1])], rows))
    return out


def is_agent(who: str) -> bool:
    w = who.lower()
    return "(fact)" in w or bool(re.match(r"(the\s+)?(agent|claude|ai)\b", w))


def check(text: str) -> list:
    gaps = []
    sections = split_sections(strip_comments(text))
    for name in SECTIONS:
        key = name.lower()
        if key not in sections:
            gaps.append(f"missing section: ## {name}")
        elif not sections[key] or "_pending_" in sections[key]:
            gaps.append(f"section still pending: ## {name}")

    if "decision log" in sections:
        human = []
        for header, rows in tables(sections["decision log"]):
            if "decided by" not in header:
                continue
            k = header.index("decided by")
            human += [r for r in rows if len(r) > k and r[k]
                      and "_pending_" not in " ".join(r) and not is_agent(r[k])]
        if not human:
            gaps.append("decision log has no decision made by a person")

    if "workflow v0" in sections:
        wf = sections["workflow v0"]
        if not tables(wf):
            gaps.append("Workflow v0 has no step table")
        if not re.search(r"N\s*=\s*1", wf):
            gaps.append("Workflow v0 has no N=1 run note")

    if "next moves" in sections:
        items = re.findall(r"^\s*(?:[-*]|\d+\.)\s+\S", sections["next moves"], re.M)
        if len(items) < 3:
            gaps.append(f"Next moves has {len(items)} list items; needs 3")
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
