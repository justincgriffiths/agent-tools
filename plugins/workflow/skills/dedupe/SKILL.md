---
name: dedupe
description: Find and resolve duplicated/nested file trees across repos — one canonical source, many vendored copies — and produce a report a HUMAN can approve in minutes. Use when the user says "dedupe", "deduplicate", "are these copies the same", "which one is canonical", "nested copies", "clean up duplicate templates", or when a repo has a directory that mirrors another repo. Also use BEFORE committing any directory that looks like a copy of something else.
argument-hint: "the two trees, or just the one you're suspicious of — the rest gets asked"
intake:
  verbs:    [scan, vendor, apply]
  required: [canonical]
  optional: [vendored, report, context]
created: 2026-07-27
source: "extracted from the author's working sessions, 2026 — a monorepo cleanup where a vendored template copy was a 94% duplicate of its canonical library (102/108 identical, 6 drifted, 0 unique) with zero provenance"
summary: "Find and resolve duplicated/nested file trees across repos — one canonical source, many vendored copies — and produce a report a human can approve in minutes"
group: "Capture & meta"
---

# dedupe — one canonical tree, many honest copies

The failure this prevents: a directory gets copied into another repo "so the team can
use it", nobody stamps where it came from, and months later nobody can answer *which
one is real*. When we found it in an agency monorepo, the copy was 94% byte-identical to the
master with 6 files silently drifted — and it was about to be committed as if it were
original work.

**The human is the point.** The user and their teammates have to approve these decisions, and
they will not read 108 diffs. So the whole system is built to shrink the review down to
*only the files that genuinely need a person*, present them side by side, and make the
default disposition obvious. A good run puts 2 numbers in front of a reviewer, not 200.

## Gathering the inputs

Three things start a run: **which tree is canonical**, **which is the suspected copy**, and
**what you want done** — scan and report, re-vendor, or apply an approved report. Take
whatever the request states and ask for the rest with the native question picker. Never make
the human type a flag.

The mode is usually inferable and shouldn't be asked: no report exists yet → scan. A report
exists with winners picked → apply. When two paths are ambiguous, put the candidates in the
options rather than asking someone to type them.

**Never guess which tree is canonical.** Backwards, this re-vendors the master *from* the copy
and destroys the source of truth. If it isn't stated and isn't obvious from provenance stamps,
that is always a question — the one input worth interrupting for.

## The three ideas

1. **Canonical vs vendored.** Exactly one tree is the source of truth. Every other copy
   is *vendored* — a deliberate, stamped, refreshable subset. There is no third category.
   A copy with no stamp is a bug, not a copy.
2. **Verdicts, not diffs.** Every file lands in one of five named buckets. Four of them
   have an automatic disposition. Only `DRIFTED` and `ORPHAN` cost a human anything.
3. **Never delete to dedupe.** Re-vendoring replaces; it does not reconcile. Anything
   that exists only in the copy gets rescued or explicitly discarded *on the record*
   first.

## Verdict taxonomy (the naming convention)

| Verdict | Meaning | Disposition | Human? |
|---|---|---|---|
| `IDENTICAL` | Same relative path, same bytes | Re-vendor from canonical. Nothing is lost. | no |
| `DRIFTED` | Same path, different bytes | **Pick a winner: `canonical` / `vendored` / `both`** | **yes** |
| `ORPHAN` | Only in the vendored copy | **Rescue upstream or discard on the record** | **yes** |
| `UPSTREAM-ONLY` | Only in canonical | Out of allowlist scope. Confirm that's intentional. | glance |
| `NESTED-REPO` | A git checkout inside another repo | **Never content.** `.gitignore` it — never delete, never commit. | no |

`GENERATED` (build output, caches, exports) is pruned before scanning, not verdicted —
see the prune list at the top of `scripts/scan-tree.sh`.

## File & naming convention

| Thing | Path | Why |
|---|---|---|
| Provenance stamp | `<vendored-root>/VENDORED.yml` | The one file that makes a copy legible. See below. |
| Review report | `data/dedupe/YYYY-MM-DD-<family>.md` | Dated, per-family, human-first. The product. |
| Verdict rows | `data/dedupe/YYYY-MM-DD-<family>.tsv` | Machine-readable audit trail. |
| Run log | `scripts/scan-tree.log` | One line per invocation, ISO timestamp + counts. |

`<family>` is the canonical tree's short name (`templates`, `brand-kit`), never the
consumer's. Two repos vendoring the same family produce comparable reports.

### `VENDORED.yml` — the stamp

Dropped at the root of every vendored copy. Without it, drift is undetectable and the
next person cannot tell a copy from an original.

```yaml
# This directory is a VENDORED COPY. Do not edit here — edit canonical and re-vendor.
canonical: git@github.com:acme/templates.git
canonical_path: <templates-repo>
synced_at: 2026-07-27
synced_commit: 2a0596c            # upstream SHA at sync time — this is what makes drift computable
allowlist:                         # which subset this repo carries, and why
  - contracts/**                   # teammates draft SOWs from these
  - reports/**
  - _shared/**                     # required by everything above
excluded:
  - pitches/**                     # this repo uses a pitch-builder skill instead
owner: dana                        # who re-vendors
```

`synced_commit` is the load-bearing field. It turns "are these the same?" from a guess
into a computation.

## Operations

### Op 1 — Scan (always first, always safe)

```
${CLAUDE_PLUGIN_ROOT}/skills/dedupe/scripts/scan-tree.sh \
  --canonical <templates-repo> --vendored <consumer-repo>/templates/library --name templates
```

Read-only. Writes only the report + tsv (to `./data/dedupe/` by default; `--out <dir>` overrides). Prints a one-line summary and exits 0 even when
it finds problems — findings are not errors.

The report leads with **"Your call is needed on N files"**. If N is 0, say so and stop;
re-vendoring is safe. If N > 0, the reviewer reads only the DRIFTED and ORPHAN sections.

The `Looks like` column is an **mtime heuristic only** — "vendored is stale" means
canonical is newer *and* same-or-longer. It is a hint to speed up review, never a reason
to skip it, and it is never auto-applied. mtime is not provenance; `synced_commit` is.

### Op 2 — Review (the human step)

Hand the reviewer the report. They fill the `Winner` column. That is the entire ask.

Present it as: *"N of M files are identical and need nothing. Here are the K that don't
match — pick a side."* Never make them scroll past the 102 files that were fine.

If every DRIFTED row reads "vendored is stale", say that out loud — it usually means one
`canonical` answer covers all of them, and the review collapses to a single yes.

### Op 3 — Sync (apply the decision)

**Do not write a new copier if the family already has one** — look for an existing sync
script in the canonical repo first (see the note at the end). Whatever copies the tree
should, at minimum:

- read the consumer's `VENDORED.yml` `allowlist:` and sync only those paths (directories
  mirrored with `--delete`, root-level files copied singly without it);
- keep `VENDORED.yml` out of `--delete` so the stamp survives;
- re-stamp `synced_at` / `synced_commit` after a successful apply;
- default to a dry run, with an explicit `--apply`.

**The interlock must be wired, not advisory:** the apply step runs `scan-tree.sh` per
consumer and **refuses (non-zero exit)** if any DRIFTED or ORPHAN file exists. A `--force`
override means "I accept losing those files."

Three ways a sync script lost data before it was hardened — test any copier against them:
- An allowlist that parsed to zero entries **failed open** into a whole-library
  `rsync --delete`. A stray trailing space after `allowlist:` or CRLF line endings was
  enough. Now: a `VENDORED.yml` that exists but parses empty is a hard error.
- `foo/../**` normalized to `foo/..` and a bare `..` escaped the subtree entirely —
  reproduced deleting an unrelated consumer file and recursively copying `$HOME` into a
  git-tracked repo. Now: `assert_safe_path` rejects `.`, `..`, any `../`, absolute paths,
  and embedded newlines.
- The orphan interlock existed only as a header comment. It is now an actual gate.

For a family that already has a sync tool, add the new consumer to it rather than
building a second mechanism.

### Op 4 — Prevent

- Add `VENDORED.yml` to any copy that lacks one *before* doing anything else.
- Nested sibling git repos go in `.gitignore` with a comment saying why. Never commit,
  never delete.
- Before committing any directory that mirrors another, run Op 1. This is the cheap
  check that would have caught the near-miss described at the top.

## Red lines

- **Never `rm -rf` a vendored tree to "clean up".** Re-vendor over it, after Op 1 shows
  zero unresolved orphans.
- **Never resolve DRIFTED without a human.** Even when the heuristic is confident. The
  files most likely to drift legitimately are exactly the ones with local context —
  `README.md`, `CLAUDE.md`, `MANIFEST.yml`.
- **Never delete a nested git repo.** It is someone's checkout with its own uncommitted
  state. `.gitignore` is the whole remedy.
- **Never commit a copy without a stamp.** An unstamped copy is the bug this skill exists
  to prevent.
- **mtime is a hint, `synced_commit` is the fact.** Do not let the `Looks like` column
  become the decision.

## Boundaries (MECE with siblings)

- Knowledge-vault hygiene — top-level shape, nested-vault dumps, secret/PII sweeps — is
  *single-vault and structural*. `dedupe` is *cross-repo and content-level*: it answers "are these two
  trees the same, and which wins". If it's "is this a copy of that", it's here.
- **`doc-maintenance`** finds stale *references* (dead paths, index drift) and stages
  backlog cards. `dedupe` finds duplicated *content*. A stale link is doc-maintenance; a
  stale copy is dedupe.
- **`learn`** Mode B audits the skill library for overlap. That's skills; this is files.

## Related

- `references/report-format.md` — the report contract, column by column
- `scripts/scan-tree.sh` — Op 1 scanner (read-only). **The only tool this skill owns.**

### A note on this skill's own history

The first draft shipped a `vendor.sh` that duplicated an existing sync script — which had
existed in the canonical repo all along, invisible because the working branch was 20
commits behind `origin/main`. It was deleted and its two genuinely-new ideas (per-consumer
allowlist, provenance stamp) were folded into the existing script. Shipping a second
copier inside a deduplication skill would have been the joke that writes itself. **Check
for the tool before building it** — the same 20-commits-behind blindness that hides a
script is what lets a duplicate tree survive.
