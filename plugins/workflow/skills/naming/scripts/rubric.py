#!/usr/bin/env python3
"""Score a library unit against the house rubric.

A filter: unit path(s) on argv -> one scored line per unit on stdout.
Exit code is the verdict: 0 every unit at or above --min, 1 at least one below,
2 the tool could not run (bad path, unknown library).

Library kinds: skills (SKILL.md), routines (ROUTINE.md), templates
(<category>/<unit>/TEMPLATE.md), prompts (<category>/<unit>.md). The kind is
inferred from the path (a component named e.g. `skills` or `skill-library`) or
from the entry docs found; pass `--kind <kind>` to force it.

Ten mechanical dimensions, 0/1/2 each, 20 points. Six judgment dimensions are
NOT scored -- they are printed as review prompts, because a script that scored
them would be guessing. That split is the honest part.

Stdlib only, on purpose: a stock /usr/bin/python3 often has no pyyaml, and a
sibling linter should be able to take the same vow.
"""
import os
import re
import sys

# ---------------------------------------------------------------- the canon

# One spelling per concept. Measured 2026-09-17 against one skill library's origin/main:
# 366 distinct `##` headings across 442 instances, 331 of them used exactly once.
# The gotchas concept alone was spelled four ways -- pitfalls 17, gotchas 8,
# don'ts 4, traps 3. These nine names replace all of it.
CANON = [
    ("when-to-fire", "When to fire"),
    ("boundaries",   "Boundaries"),
    ("map",          "Map"),
    ("procedure",    "Procedure"),
    ("verify",       "Verify"),
    ("gotchas",      "Gotchas"),
    ("origin",       "Origin"),
    ("receipts",     "Receipts"),
    ("references",   "References"),
]
CANON_SLUGS = [s for s, _ in CANON]
CANON_ORDER = {s: i for i, s in enumerate(CANON_SLUGS)}

# What each retired spelling folds into. Used by --suggest, never applied
# automatically: naming gotcha 2 -- never let a script infer which renames are safe.
RETIRED_HEADINGS = {
    "pitfalls": "gotchas", "don'ts": "gotchas", "donts": "gotchas",
    "traps": "gotchas", "failure modes": "gotchas", "known traps": "gotchas",
    "when to use": "when-to-fire", "scope": "when-to-fire",
    "run it": "procedure", "running it": "procedure", "usage": "procedure",
    "the loop": "procedure", "the pipeline": "procedure", "steps": "procedure",
    "what the gate checks": "verify", "what the gate cannot catch": "verify",
    "the verify gate": "verify",
    "see also": "references", "related": "references",
    "why this exists": "origin", "history": "origin",
    "reference implementation": "references",
    "guardrails (read first)": "gotchas",
}

# A shape is a promise about which sections the body owes. Derived from the six
# archetypes the library already had, not invented: the tree grew these, the
# rubric only names them.
# Only the sections a reader HUNTS for under pressure are required by name.
# Origin and Receipts are deliberately NOT required anywhere: provenance is a
# frontmatter job (`source:`, `verified:`), and a section that restates a field
# is the ceremony this rubric exists to remove.
SHAPES = {
    # judgment essay forged by one incident -- "verify before you delete"
    "judgment": {"gotchas"},
    # operating manual for a live pipeline -- shipping a deck or a portal
    "manual":   {"map", "procedure", "verify", "gotchas"},
    # config-as-data surface guide -- one page type of an internal portal
    "surface":  {"map", "procedure", "gotchas"},
    # decision router that delegates and stops -- learn, a research router
    "router":   {"map", "boundaries"},
    # house-deliverable spec -- a pitch-deck or statement-of-work spec
    "spec":     {"verify", "gotchas"},
    # reference hub whose body is a table of contents -- an index of frameworks
    "hub":      {"references"},
}

ENTRY_DOC = {
    "skills": "SKILL.md",
    "routines": "ROUTINE.md",
    "templates": "TEMPLATE.md",
    "prompts": None,  # the unit IS the .md
}
# Directory names that identify a library kind: `skills`, `skill-library`, ...
ALIASES = {}
for _k in ENTRY_DOC:
    ALIASES[_k] = _k
    ALIASES[_k[:-1] + "-library"] = _k
MAX_LINES = {"skills": 300, "prompts": 400, "routines": 300, "templates": 300}
DESC_MAX_CHARS = 1024

ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# A description must describe CONDITIONS, not summarise the body. Deliberately
# broad: the first draft demanded `use this when` and scored the `naming` skill's
# own "when a name feels arbitrary" as triggerless. A narrow trigger regex
# produces confident false negatives, which is worse than a loose one -- the
# tight judgment call is `does-it-fire`, and that one is not scored at all.
TRIGGER = re.compile(
    r"\buse (this|it)\b|\buse for\b|\btrigger|\bfire\b|\bwhenever\b|"
    r"\bwhen\b|\bbefore\b|\bafter\b|\bload (before|when)\b|"
    r"\bany time\b|\beach time\b", re.I)
BOUNDARY = re.compile(
    r"\bSKIP\b|\bNOT for\b|\bdo not use\b|\bdon't use\b|\bnever use\b|"
    r"\binstead\b|\bboundar|\brather than\b")
INCIDENT = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\borigin\b|\bcost\b|\bpaid for\b", re.I)

# ------------------------------------------------------------------ parsing


def split_front(text):
    """-> (frontmatter dict of raw strings, body, total line count)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text, len(lines)
    end = None
    for i, l in enumerate(lines[1:], 1):
        if l.strip() == "---":
            end = i
            break
    if end is None:
        return None, text, len(lines)
    fm, key = {}, None
    for l in lines[1:end]:
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", l)
        if m:
            key = m.group(1)
            fm[key] = m.group(2)
        elif key and l[:1] in (" ", "\t"):
            fm[key] = (fm[key] + " " + l.strip()).strip()
    return fm, "\n".join(lines[end + 1:]), len(lines)


def h2s(body):
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", body, re.M)]


def slugify_heading(h):
    """Map a heading onto a canon slug, or None if it is not a canon section.

    None is NOT a violation. A free H2 is where the argument lives --
    `## Noticing is not filing` is the best line in `deprecate-on-sight` and a
    whitelist that flattened it into `## Gotchas` would destroy the document to
    satisfy the checker. The canon is a required SUBSET, never an allow-list.
    Only a RETIRED SPELLING is a violation, because that is a second name for a
    concept the canon already named.
    """
    low = h.strip().lower().rstrip(":")
    low = re.sub(r"\s*[-–—(].*$", "", low).strip()  # drop parentheticals/dashes
    for slug, disp in CANON:
        if low == disp.lower() or low == slug:
            return slug
    return None


def retired_heading(h):
    """-> the canon name this heading should have used, or None."""
    low = h.strip().lower().rstrip(":")
    low = re.sub(r"\s*[-–—(].*$", "", low).strip()
    return RETIRED_HEADINGS.get(low)


def section_body(body, slug):
    """Text under the canon section, or '' if absent."""
    disp = dict(CANON)[slug]
    m = re.search(r"^##\s+%s.*$" % re.escape(disp), body, re.M | re.I)
    if not m:
        return ""
    rest = body[m.end():]
    nxt = re.search(r"^##\s+", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


# ---------------------------------------------------------------- the score

DIMENSIONS = [
    ("identity",   "name is kebab-case, matches its directory, entry doc present"),
    ("provenance", "created: and source: present, created: is an ISO date"),
    ("routing",    "description present, within %d chars, states when to fire" % DESC_MAX_CHARS),
    ("boundary",   "says when NOT to fire -- in the description or a Boundaries section"),
    ("shape",      "declares a known shape:, owes no section, uses no retired heading"),
    ("gotchas",    "a Gotchas section whose entries carry their incident"),
    ("gate",       "a Verify section that also states what the gate cannot catch"),
    ("evidence",   "a verified: ISO date, or a Receipts section that carries dates"),
    ("size",       "within the library line cap, with detail pushed to references/"),
    ("contract",   "invocation declared as intake:, not a bare argument-hint:"),
]
JUDGMENT = [
    "library-fit:  would anything be lost if this sat in a sibling library?",
    "name-quality: does the name say the job, with no 'and', no client, no version?",
    "does-it-fire: would the description actually win the trigger it wants?",
    "source-true:  is source: the real provenance, or a plausible guess?",
    "mece-real:    is the declared boundary true of the sibling's body today?",
    "gotchas-real: is each gotcha a paid-for incident, or a generic caution?",
]


def score_unit(path, lib):
    """-> (dict of dimension -> (points, note), meta)."""
    entry = ENTRY_DOC.get(lib)
    if entry is None:
        doc = path
        unit = os.path.basename(path)[:-3] if path.endswith(".md") else os.path.basename(path)
    else:
        doc = os.path.join(path, entry)
        unit = os.path.basename(path.rstrip("/"))
    if not os.path.isfile(doc):
        return None, {"unit": unit, "error": "no entry doc at %s" % doc}

    text = open(doc, encoding="utf-8", errors="replace").read()
    fm, body, nlines = split_front(text)
    fm = fm or {}
    heads = h2s(body)
    present = {s for s in (slugify_heading(h) for h in heads) if s}
    retired = [(h, retired_heading(h)) for h in heads if retired_heading(h)]
    shape = (fm.get("shape") or "").strip()
    desc = (fm.get("description") or "").strip().strip("\"'")
    S = {}

    # 1 identity
    ok_kebab = bool(KEBAB.match(unit))
    ok_name = fm.get("name", "").strip() == unit
    S["identity"] = (2 if (ok_kebab and ok_name) else 1 if ok_kebab else 0,
                     "" if (ok_kebab and ok_name) else
                     "name: %r != dir %r" % (fm.get("name", ""), unit) if ok_kebab
                     else "not kebab-case")

    # 2 provenance
    has_c, has_s = "created" in fm, "source" in fm
    iso = ISO.match(fm.get("created", "").strip() or "x") is not None
    S["provenance"] = (2 if (has_c and has_s and iso) else 1 if (has_c or has_s) else 0,
                       "" if (has_c and has_s and iso) else
                       ", ".join(filter(None, [
                           "" if has_c else "no created:",
                           "" if has_s else "no source:",
                           "" if iso or not has_c else "created: not ISO"])))

    # 3 routing
    if not desc:
        S["routing"] = (0, "no description:")
    elif len(desc) > DESC_MAX_CHARS:
        S["routing"] = (1, "description %d chars > %d" % (len(desc), DESC_MAX_CHARS))
    elif not TRIGGER.search(desc):
        S["routing"] = (1, "description states no trigger")
    else:
        S["routing"] = (2, "")

    # 4 boundary -- mandatory once a prefix sibling exists; the rubric cannot
    # see siblings from one unit, so --all supplies them via FAMILY.
    in_desc = bool(desc and BOUNDARY.search(desc))
    in_body = "boundaries" in present
    fam = FAMILY.get(unit.split("-")[0], 0) >= 2
    if in_desc or in_body:
        S["boundary"] = (2, "")
    elif not fam:
        S["boundary"] = (2, "n/a -- no prefix sibling to be confused with")
    else:
        S["boundary"] = (0, "in a %s-* family and states no boundary" % unit.split("-")[0])

    # 5 shape
    if shape not in SHAPES:
        S["shape"] = (0, "no shape: declared (one of %s)" % "|".join(sorted(SHAPES)))
    elif retired:
        S["shape"] = (1, "retired heading spelling: %s" % "; ".join(
            "'%s' -> %s" % (h, c) for h, c in retired[:3]))
    else:
        missing = SHAPES[shape] - present
        S["shape"] = (2, "") if not missing else (
            1, "shape %s owes: %s" % (shape, ", ".join(sorted(missing))))

    # 6 gotchas
    g = section_body(body, "gotchas")
    if not g.strip():
        S["gotchas"] = (0, "no Gotchas section")
    elif not INCIDENT.search(g):
        S["gotchas"] = (1, "Gotchas carry no date or incident")
    else:
        S["gotchas"] = (2, "")

    # 7 gate
    v = section_body(body, "verify")
    needs_gate = shape in ("manual", "surface", "spec") or lib == "routines"
    if v.strip():
        cannot = re.search(r"cannot|can't|does not catch|by eye|not automated|human",
                           v, re.I)
        S["gate"] = (2, "") if cannot else (1, "Verify does not say what it cannot catch")
    else:
        S["gate"] = ((0, "no Verify section") if needs_gate
                     else (2, "n/a -- shape %s produces no gated artifact"
                           % (shape or "?")))

    # 8 evidence
    has_r = bool(section_body(body, "receipts").strip())
    ver = fm.get("verified", "").strip()
    dated = bool(ISO.match(ver)) if ver else False
    if dated or (has_r and INCIDENT.search(section_body(body, "receipts"))):
        S["evidence"] = (2, "")
    elif has_r or ver:
        S["evidence"] = (1, "verified: %r is not an ISO date" % ver if ver
                         else "Receipts section carries no date")
    else:
        S["evidence"] = (0, "nothing says what was verified, or when")

    # 9 size
    cap = MAX_LINES.get(lib, 300)
    has_refs = (entry is not None
                and os.path.isdir(os.path.join(path, "references")))
    if nlines <= cap:
        S["size"] = (2, "")
    elif has_refs:
        S["size"] = (1, "%d lines > %d (references/ exists -- move more)" % (nlines, cap))
    else:
        S["size"] = (0, "%d lines > %d and no references/" % (nlines, cap))

    # 10 contract
    if "argument-hint" in fm and "intake" not in fm:
        S["contract"] = (0, "argument-hint: without intake: -- the harness reads neither")
    elif "intake" in fm:
        S["contract"] = (2, "")
    else:
        S["contract"] = (2, "n/a -- takes no arguments")

    total = sum(p for p, _ in S.values())
    return S, {"unit": unit, "lib": lib, "shape": shape or "-",
               "lines": nlines, "desc": len(desc), "total": total}


# --------------------------------------------------------------------- main

FAMILY = {}
FORCED_KIND = None


def resolve_library(path):
    """Name the library kind owning `path`, or None.

    Strategies, in order. Taking only the path's basename is the bug a
    basename-based linter has: a linked worktree's basename is its slug
    (`unit-grammar-devbox`, `live`), never the library name, so it fails on
    every worktree checkout. This function was written after the same bug bit
    this file -- see references/enforcement.md.
    """
    if FORCED_KIND:
        return FORCED_KIND
    path = os.path.abspath(path.rstrip("/"))
    # 1. the path itself names a library, at any depth
    #    <home>/skill-library/x, <worktrees>/skills/live/x
    parts = path.split(os.sep)
    for comp in reversed(parts):
        if comp in ALIASES:
            return ALIASES[comp]
    # 2. a linked worktree: the common git dir's parent is the main checkout,
    #    whose basename IS the library. <home>/skill-library/.claude/worktrees/slug
    try:
        import subprocess
        common = subprocess.run(
            ["git", "-C", path, "rev-parse", "--path-format=absolute",
             "--git-common-dir"],
            capture_output=True, text=True, timeout=5)
        if common.returncode == 0:
            root = os.path.basename(os.path.dirname(
                os.path.abspath(common.stdout.strip())))
            if root in ALIASES:
                return ALIASES[root]
    except Exception:
        pass
    # 3. an entry doc we recognise: the path is a unit
    for lib, entry in ENTRY_DOC.items():
        if entry and os.path.isfile(os.path.join(path, entry)):
            return lib
    # 4. entry docs one or two levels down: the path is a library root
    if os.path.isdir(path):
        kids = [os.path.join(path, k) for k in sorted(os.listdir(path))
                if not k.startswith(".") and os.path.isdir(os.path.join(path, k))]
        for lib in ("skills", "routines"):
            if any(os.path.isfile(os.path.join(k, ENTRY_DOC[lib])) for k in kids):
                return lib
        for k in kids:
            if any(os.path.isfile(os.path.join(k, u, "TEMPLATE.md"))
                   for u in os.listdir(k)):
                return "templates"
    return None


def discover(lib_path):
    lib = resolve_library(lib_path)
    if lib not in ENTRY_DOC:
        sys.stderr.write("not a known library: %s\n" % lib)
        return lib, []
    entry = ENTRY_DOC[lib]
    out = []
    if entry is None:
        for cat in sorted(os.listdir(lib_path)):
            d = os.path.join(lib_path, cat)
            if not os.path.isdir(d) or cat.startswith((".", "_")):
                continue
            out += [os.path.join(d, f) for f in sorted(os.listdir(d))
                    if f.endswith(".md") and f not in ("README.md", "CLAUDE.md")]
    elif lib == "templates":
        for cat in sorted(os.listdir(lib_path)):
            d = os.path.join(lib_path, cat)
            if not os.path.isdir(d) or cat.startswith((".", "_")):
                continue
            out += [os.path.join(d, u) for u in sorted(os.listdir(d))
                    if os.path.isfile(os.path.join(d, u, entry))]
    else:
        out = [os.path.join(lib_path, u) for u in sorted(os.listdir(lib_path))
               if os.path.isfile(os.path.join(lib_path, u, entry))]
    return lib, out


def print_table():
    print("| Dimension | 2 points means |")
    print("|---|---|")
    for k, d in DIMENSIONS:
        print("| `%s` | %s |" % (k, d))
    print()
    print("| Shape | Sections it owes |")
    print("|---|---|")
    for s in sorted(SHAPES):
        print("| `%s` | %s |" % (s, ", ".join(sorted(SHAPES[s])) or "—"))


def main(argv):
    if "--print-table" in argv:
        print_table()
        return 0
    global FORCED_KIND
    verbose = "-v" in argv or "--verbose" in argv
    review = "--review" in argv
    try:
        minimum = int(argv[argv.index("--min") + 1])
    except (ValueError, IndexError):
        minimum = 16
    if "--kind" in argv:
        i = argv.index("--kind")
        FORCED_KIND = argv[i + 1] if i + 1 < len(argv) else None
        if FORCED_KIND not in ENTRY_DOC:
            sys.stderr.write("--kind must be one of: %s\n" % ", ".join(ENTRY_DOC))
            return 2
        argv = argv[:i] + argv[i + 2:]
    targets = [a for a in argv[1:] if not a.startswith("-")
               and not a.isdigit()]
    if not targets:
        sys.stderr.write("usage: rubric.py <library-or-unit> [...] "
                         "[--min N] [--kind skills|routines|templates|prompts] "
                         "[-v] [--review] [--print-table]\n")
        return 2

    units = []
    for tgt in targets:
        tgt = os.path.abspath(tgt)
        lib = resolve_library(tgt)
        if lib is None:
            sys.stderr.write("cannot resolve a library for %s\n" % tgt)
            return 2
        # is `tgt` the library root, or one unit inside it?
        entry = ENTRY_DOC[lib]
        is_unit = (tgt.endswith(".md") if entry is None
                   else os.path.isfile(os.path.join(tgt, entry)))
        if is_unit:
            units.append((lib, tgt))
        else:
            lib, found = discover(tgt)
            if not found:
                return 2
            units += [(lib, f) for f in found]

    for lib, u in units:
        name = os.path.basename(u.rstrip("/"))
        FAMILY[name.split("-")[0]] = FAMILY.get(name.split("-")[0], 0) + 1

    rows, failed = [], 0
    for lib, u in units:
        S, meta = score_unit(u, lib)
        if S is None:
            print("ERROR\t%s\t%s" % (meta["unit"], meta["error"]))
            failed += 1
            continue
        grade = ("A" if meta["total"] >= 18 else "B" if meta["total"] >= 16
                 else "C" if meta["total"] >= 12 else "D")
        if meta["total"] < minimum:
            failed += 1
        rows.append((meta, S, grade))
        print("%s\t%2d/20\t%-9s\t%-28s\t%s" % (
            grade, meta["total"], meta["shape"], meta["unit"],
            " ".join("%s=%d" % (k, S[k][0]) for k, _ in DIMENSIONS)))
        if verbose:
            for k, _ in DIMENSIONS:
                pts, note = S[k]
                if pts < 2:
                    print("        %-11s %d  %s" % (k, pts, note))

    if rows:
        avg = sum(m["total"] for m, _, _ in rows) / float(len(rows))
        print("\n%d units  mean %.1f/20  below --min %d: %d"
              % (len(rows), avg, minimum, failed))
        worst = {}
        for _, S, _ in rows:
            for k, _d in DIMENSIONS:
                worst[k] = worst.get(k, 0) + S[k][0]
        print("weakest dimensions: " + ", ".join(
            "%s %.1f" % (k, worst[k] / float(len(rows)))
            for k in sorted(worst, key=lambda k: worst[k])[:4]))
    if review:
        print("\nJudgment -- not scored, ask these by hand:")
        for j in JUDGMENT:
            print("  " + j)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
