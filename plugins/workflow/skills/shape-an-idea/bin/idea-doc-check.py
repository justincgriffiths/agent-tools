#!/usr/bin/env python3
"""idea-doc-check — does a shape-an-idea doc clear the bar?

Filter: reads the doc from the path argument (or stdin when the path is '-'), prints one
line per gap, and exits 1 on any gap, 0 when the doc is complete, 2 on a usage error.

  python3 bin/idea-doc-check.py docs/ideas/<slug>.md

Complete means:
  - all seven sections are present (headings match case-insensitively), none still _pending_
    (text inside HTML comments is ignored)
  - the decision log has at least one decision the person made in this session: its
    "Decided by" cell (found by header) is not an agent, not "(fact)", not "carried"
  - autopilot docs (header line "mode: autopilot") record "Overturned: N of M"
  - Deliverables and timeline holds two tables (deliverables, timeline)
  - Work packages holds a table with Tier, Est. min and Acceptance columns; every row has a
    known tier, a numeric estimate and a non-empty acceptance check
  - Dry-fire ends in "Result: pass" or "Result: re-tiered to <tier> ..."
"""
import re
import sys

SECTIONS = [
    "Problem statement",
    "Decision log",
    "Assumptions",
    "Research",
    "Deliverables and timeline",
    "Work packages",
    "Dry-fire",
]
TIERS = {"script", "small", "mid", "frontier", "human"}
SEP = re.compile(r"^\|(\s*:?-{2,}:?\s*\|)+\s*$")


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


def cells(line: str) -> list:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def tables(body: str) -> list:
    """Every markdown table in body as (header_cells_lowercased, data_rows)."""
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


def col(header: list, *names: str):
    for i, h in enumerate(header):
        if any(h.startswith(n) for n in names):
            return i
    return None


def not_in_session(who: str) -> bool:
    w = who.lower()
    return ("(fact)" in w or "(assumed" in w or w.startswith("carried")
            or bool(re.match(r"(the\s+)?(agent|claude|ai)\b", w)))


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
        log = sections["decision log"]
        human = []
        for header, rows in tables(log):
            k = col(header, "decided by")
            if k is None:
                continue
            human += [r for r in rows if len(r) > k and r[k]
                      and "_pending_" not in " ".join(r) and not not_in_session(r[k])]
        if not human:
            gaps.append("decision log has no decision the person made in this session")
        if re.search(r"mode:\s*autopilot", text, re.I) and not re.search(r"Overturned:\s*\d+\s+of\s+\d+", log):
            gaps.append("autopilot doc has no 'Overturned: N of M' line in the decision log")

    if "deliverables and timeline" in sections:
        if len(tables(sections["deliverables and timeline"])) < 2:
            gaps.append("Deliverables and timeline needs two tables (deliverables, timeline)")

    if "work packages" in sections:
        pkg = [(h, r) for h, r in tables(sections["work packages"]) if col(h, "tier") is not None]
        if not pkg:
            gaps.append("Work packages has no package table with a Tier column")
        for header, rows in pkg:
            t, e, a = col(header, "tier"), col(header, "est"), col(header, "acceptance")
            if e is None or a is None:
                gaps.append("package table needs Est. min and Acceptance columns")
                continue
            if not rows:
                gaps.append("package table has no packages")
            for r in rows:
                pid = r[0] if r else "?"
                if len(r) <= max(t, e, a):
                    gaps.append(f"package {pid}: row has missing cells")
                    continue
                if r[t].lower() not in TIERS:
                    gaps.append(f"package {pid}: tier '{r[t]}' is not one of {sorted(TIERS)}")
                if not re.fullmatch(r"\d+", r[e]):
                    gaps.append(f"package {pid}: Est. min '{r[e]}' is not a number")
                if not r[a] or r[a] in {"-", "–"}:
                    gaps.append(f"package {pid}: no acceptance check")

    if "dry-fire" in sections:
        if not re.search(r"^Result:\s*(pass\b|re-tiered to\s+\w+)", sections["dry-fire"], re.M | re.I):
            gaps.append("Dry-fire has no 'Result: pass' or 'Result: re-tiered to <tier>' line")
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
