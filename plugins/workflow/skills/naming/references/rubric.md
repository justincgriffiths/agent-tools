# The rubric — scoring a unit

Ten dimensions, 0/1/2 each, **20 points**. Run it; do not eyeball it.

```sh
R=${CLAUDE_PLUGIN_ROOT}/skills/naming/scripts/rubric.py
$R <library>                     # whole library
$R <unit> -v --review             # one unit, in detail
$R <library> --min 16             # exit 1 if any unit is below
$R <library> --kind skills        # force the library kind if it cannot be inferred
```

The library kind (skills, routines, templates, prompts) is inferred from a path component
such as `skills` or `skill-library`, or from the entry docs it finds.

**Check the path resolves before you document it.** An advertised
`~/.claude/skills/naming` symlink once pointed at a detached worktree 40 commits behind
`origin/main`, so the documented invocation failed — verified 2026-09-17, `ls` returned
*No such file or directory*. A tool whose documented invocation fails is the same defect as
`CLAUDE.md` files pointing at a script path that does not exist.

It is a filter: units on argv, one scored line per unit on stdout, **exit code
is the verdict** — `0` all units at or above `--min` (default 16), `1` at least
one below, `2` the tool could not run. No writes, ever.

## What the score means

| Grade | Points | Reading |
|---|---|---|
| **A** | 18–20 | conformant; the grammar is doing its job |
| **B** | 16–17 | one soft gap, usually `evidence` or `boundary` |
| **C** | 12–15 | pre-grammar writing; migrate it |
| **D** | 0–11 | pre-grammar *and* missing frontmatter the block tier will reject |

**A low grade is a migration distance, not a verdict on the writing.**
`verify-before-delete` is one of the best-argued documents in the library and
scores 9/20, because every dimension it fails is a field or a section name that
did not exist when it was written. Grade the *unit*; judge the *prose* by hand.

## The ten dimensions

<!-- BEGIN generated-table: rubric.py --print-table -->
| Dimension | 2 points means |
|---|---|
| `identity` | name is kebab-case, matches its directory, entry doc present |
| `provenance` | created: and source: present, created: is an ISO date |
| `routing` | description present, within 1024 chars, states when to fire |
| `boundary` | says when NOT to fire -- in the description or a Boundaries section |
| `shape` | declares a known shape:, owes no section, uses no retired heading |
| `gotchas` | a Gotchas section whose entries carry their incident |
| `gate` | a Verify section that also states what the gate cannot catch |
| `evidence` | a verified: ISO date, or a Receipts section that carries dates |
| `size` | within the library line cap, with detail pushed to references/ |
| `contract` | invocation declared as intake:, not a bare argument-hint: |

| Shape | Sections it owes |
|---|---|
| `hub` | references |
| `judgment` | gotchas |
| `manual` | gotchas, map, procedure, verify |
| `router` | boundaries, map |
| `spec` | gotchas, verify |
| `surface` | gotchas, map, procedure |
<!-- END generated-table -->

**Not-applicable scores 2.** A `judgment`-shaped unit owes no gate; a unit that
takes no arguments owes no `intake:`; a unit with no prefix sibling owes no
boundary. Each scores full marks with an `n/a` note, because a rubric whose top
grade is unreachable by shape teaches people to ignore it.

## The six it refuses to score

A script scoring these would be guessing, so it prints them as questions
instead (`--review`):

- **library-fit** — would anything be lost if this sat in a sibling library?
- **name-quality** — does the name say the job, with no "and", no client, no version?
- **does-it-fire** — would this description actually win the trigger it wants, against its siblings?
- **source-true** — is `source:` the real provenance, or a plausible guess?
- **mece-real** — is the declared boundary still true of the sibling's body *today*?
- **gotchas-real** — is each gotcha a paid-for incident, or a generic caution?

`mece-real` is the one that decays without anyone touching the file: a boundary
written against a sibling is a claim about *another* document, and nothing
tells you when that document moved.

## Baseline

**Measured 2026-09-17** against `origin/main` of each library, exported clean
(`git archive`) of the source libraries rather than read from the working checkouts, which are 205, 71,
9 and 11 commits behind:

| Library | Units | Mean | Below 16 | Weakest dimensions |
|---|---|---|---|---|
| skills | 59 | **13.5** | 50 | `shape` 0.0 · `evidence` 0.2 · `gotchas` 0.3 · `boundary` 1.6 |
| routines | 18 | **10.9** | 18 | `routing` 0.0 · `shape` 0.0 · `gate` 0.1 · `evidence` 0.1 |
| templates | 39 | **11.3** | 39 | `routing` 0.0 · `shape` 0.0 · `gotchas` 0.0 · `evidence` 0.3 |
| prompts | 15 | **13.3** | 15 | `shape` 0.0 · `gotchas` 0.0 · `evidence` 0.0 · `boundary` 1.6 |

Read the weakest columns rather than the means — they say what the libraries
actually lack:

- **`shape` 0.0 everywhere** is expected, not damning: the field is new. It is
  the one dimension a mechanical pass can fix.
- **`gotchas` near zero** is a *spelling* result, not an absence. 38 of 59
  skills have a trap list; they call it `Pitfalls`, `Don'ts` or `Traps`.
- **`routing` 0.0 in the routine and template libraries** is real and structural:
  neither library has a `description:` field at all, so neither can express when
  to fire. `reports/one-pager` and `pitches/one-pager` collide on name with
  nothing to disambiguate them — that is what its absence costs.
- **`boundary` 1.6 in the skill library** is 12 of the 16 units inside a
  `<product>-*` / `<subsystem>-*` / `<client>-*` family failing to say when to defer to a
  sibling. Units with no sibling score `n/a`, so this number is entirely the
  families.
- **`evidence` near zero everywhere** is the honest one. Almost nothing records
  what was actually run, so almost nothing distinguishes a verified claim from
  a confident one.

## Gotchas

- **The rubric scored its own author wrong first.** The initial draft treated
  any non-canonical `##` as a violation, which would have flattened
  one judgment skill's argument headings. Caught by running it at N=1 before
  touching a second file — see [`unit-grammar.md`](unit-grammar.md).
- **`rubric.py` shipped with the linter's worktree bug and had to be fixed the
  same day.** Deriving a library from a path basename fails on every worktree
  checkout. It now walks the path, then asks
  `git rev-parse --git-common-dir`.
- **A tight trigger regex scored this skill's own author wrong.** `naming`'s
  description opens with three `when` clauses and the first pattern called it
  triggerless. The check is now deliberately loose; precision lives in the
  unscored `does-it-fire` question.
- **Scores are not comparable across libraries yet.** `routing` and `gate` are
  unearnable in a template library until it has a `description:` field, so its
  11.3 is not worse writing than the skill library's 13.5 — it is a thinner schema.

## Receipts

**Verified 2026-09-17**: run over all 131 units on `origin/main`; run from
inside a linked worktree; one judgment skill migrated and re-scored 10 → 20.
**Unverified**: never run in a pre-commit hook or a cron; not wired into a linter's
`verify` gate. The `--kind` flag and entry-doc inference were added for this public copy
and checked only against this plugin's own `skills/` directory.
