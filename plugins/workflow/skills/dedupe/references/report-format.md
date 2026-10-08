# The dedup report contract

The report is the product. Everything else in this skill exists to produce it. It is
written for **the user and their reviewers** — people who will give it two minutes.

## Design rules

1. **Lead with the ask, not the data.** The first heading is
   `## Your call is needed on N files`. A reviewer who reads nothing else knows their
   cost up front.
2. **Never make a human scroll past what was fine.** `IDENTICAL` gets one row in the
   summary table and is never enumerated. In the first real run that hid 102 files.
3. **One decision per row, one word to answer.** The `Winner` column takes
   `canonical` / `vendored` / `both`. Not prose.
4. **Every number reproducible.** The report ends with the exact command that produced
   it. If a reviewer doubts a count, they re-run it.
5. **Heuristics are labelled as heuristics.** The `Looks like` column is mtime-derived
   and says so. It speeds review; it never substitutes for it.
6. **Diffs are collapsed.** `<details>` per file, capped at 120 lines. Long diffs are a
   signal to open the file, not to paste it.

## Section order (fixed)

| # | Section | Shown when |
|---|---|---|
| 1 | Header — date, both roots, file counts, stamp present/absent | always |
| 2 | `## Your call is needed on N files` + verdict summary table | always |
| 3 | Clean-run callout | only when DRIFTED + ORPHAN = 0 |
| 4 | `## DRIFTED — pick a winner per file` + table + collapsed diffs | only when DRIFTED > 0 |
| 5 | `## ORPHAN — only in the vendored copy` + table | only when ORPHAN > 0 |
| 6 | `## Reproduce` — exact command + tsv path | always |

Sections that would be empty are omitted entirely. An empty heading is noise.

## Columns

**DRIFTED table**

| Column | Content | Note |
|---|---|---|
| `#` | Index, matches the diff below | so a reviewer can say "3 and 5 are vendored" |
| `File` | Path relative to the tree root, no `./` | |
| `Vendored` | `<lines>L · <mtime date>` | |
| `Canonical` | `<lines>L · <mtime date>` | |
| `Looks like` | `vendored is stale` / `vendored edited later` / `**genuine fork**` | heuristic; bolded only when it can't tell |
| `Winner` | blank `_______` | the reviewer fills this |

**ORPHAN table** — `File`, `Lines`, `Modified`. Deliberately sparse: the only question is
rescue or discard, and that needs the path plus a sense of whether it's substantial.

## The TSV sidecar

`VERDICT<TAB>path`, ordered DRIFTED → ORPHAN → IDENTICAL → UPSTREAM-ONLY. Ordered so
`head` shows what matters. This is what a sync script's orphan interlock reads — it is an
interlock, not just a log.

## Anti-patterns

- **A percentage as the headline.** "94% duplicate" sounds resolved. "6 files need your
  call" is actionable. Lead with the count of decisions, not the ratio.
- **Auto-resolving on mtime.** A file touched by a `cp -R` has a fresh mtime and stale
  content. This is why `synced_commit` exists.
- **Bundling families.** One report per canonical family. A combined report cannot be
  approved incrementally, so it gets approved lazily or not at all.
- **Reporting a clean run as nothing.** Say "nothing needs your review, re-vendoring is
  safe" explicitly. Silence reads as "didn't run".
