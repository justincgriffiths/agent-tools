# Unit grammar — the body and the shape

A linter schema (`schema.py` below) already governs the parts of a unit a machine could always see:
which library owns it, what its directory is called, which frontmatter fields
are legal, what `status:` may say. That half is settled and **should not be
relitigated** — read [`CHEATSHEET.md`](CHEATSHEET.md) and move on.

This page governs the half that had no rule at all: **what the document is made
of, and what a reader is entitled to find in it.**

> **The measurement that forced this page.** 59 skills on one skill library's
> `origin/main`, 2026-09-17: **442 `##` headings, 366 of them distinct, 331 used
> exactly once.** The gotchas concept alone was spelled four ways — `Pitfalls`
> ×17, `Gotchas` ×8, `Don'ts` ×4, `Traps` ×3. A reader who has broken something
> and wants the trap list has to read the whole file to find out what this
> particular author called it.

## The ten elements

Every unit in every library is made of these, whatever the library calls them:

| # | Element | Lives in | Governed by |
|---|---|---|---|
| 1 | **Identity** — which library, what name | path + `name:` | `schema.py` |
| 2 | **Provenance** — when, and where it came from | `created:` `source:` | `schema.py` |
| 3 | **Routing** — when to fire | `description:` | `schema.py` (cap) + this page (structure) |
| 4 | **Boundary** — when *not* to fire | `description:` or `## Boundaries` | this page |
| 5 | **Shape** — which archetype, hence which sections | `shape:` | this page |
| 6 | **Body** — the argument, the map, the steps | the prose | this page |
| 7 | **Gotchas** — the traps, each with its incident | `## Gotchas` | this page |
| 8 | **Gate** — the check, and what it cannot catch | `## Verify` | this page + routine `verify:` |
| 9 | **Evidence** — what was actually run, and when | `verified:` / `## Receipts` | this page |
| 10 | **Contract** — what it must be told | `intake:` | `schema.py` (grammar) |

Elements 1, 2, 10 are checked today. **3 through 9 are what this page adds.**

## Nine canonical sections

**In this order, when present:**

| `##` heading | Holds | Not |
|---|---|---|
| `When to fire` | trigger detail the description could not carry | a restatement of the description |
| `Boundaries` | the sibling contest, resolved: what goes where | a list of vaguely related units |
| `Map` | the orienting table — where things live, cue→action, symptom→cause, verdict→test | narrative |
| `Procedure` | the ordered steps, or the one command that runs them | a second copy of a routine's script |
| `Verify` | the gate, **and what the gate cannot catch** | a claim that it is correct |
| `Gotchas` | traps, each carrying the incident that paid for it | generic caution |
| `Origin` | why the unit exists, when `source:` cannot hold it | a changelog |
| `Receipts` | what was run, on what date, and what was *not* | "verified" with no object |
| `References` | pointers into `references/`, with what each answers | the output of `ls` |

**The canon is a required subset, never an allow-list.** This is the rule that
matters most, and it is the one a first draft of this page got wrong.

- **Free headings are correct.** `## Noticing is not filing` is the best line in
  `deprecate-on-sight` (a judgment skill in the source library); `## The harm is not the dead thing` carries its whole
  argument. A whitelist would have flattened both into `## Gotchas` and
  destroyed the document to satisfy a checker.
- **A shape owes certain sections by name.** Those are the ones a reader *hunts*
  for under pressure — the trap list when something breaks, the gate before
  shipping, the boundary when choosing between siblings.
- **Only a retired spelling is a violation.** Calling it `## Pitfalls` when the
  canon says `## Gotchas` is a second name for a named concept. Calling a section
  `## Why the loop stops here` is writing.

### Retired spellings

| Was | Is now |
|---|---|
| `Pitfalls` · `Don'ts` · `Traps` · `Failure modes` · `Known traps` · `Guardrails (read first)` | `Gotchas` |
| `When to use` · `Scope` | `When to fire` |
| `Run it` · `Running it` · `Usage` · `Steps` · `The loop` · `The pipeline` | `Procedure` |
| `What the gate checks` · `What the gate cannot catch` · `The verify gate` | `Verify` (both halves, one section) |
| `See also` · `Related` · `Reference implementation` | `References` |
| `Why this exists` · `History` | `Origin` |

`Failure modes` is retired **in name only** — the prompt library's
grown-per-run discipline is the thing worth keeping, and it now lives under
`## Gotchas` with the same append-on-each-run rule.

## Six shapes

A unit declares `shape:` and the owed sections follow. The shapes were not
invented: they are the six archetypes the tree already grew.

| `shape:` | What it is | Owes, by name | Typical example |
|---|---|---|---|
| `judgment` | one incident, generalized into a rule | `Gotchas` | "verify before you delete", "deprecate what you notice" |
| `manual` | operating manual for something live | `Map` `Procedure` `Verify` `Gotchas` | shipping a deck or an internal portal |
| `surface` | config-as-data guide to one surface | `Map` `Procedure` `Gotchas` | one page type of an internal portal |
| `router` | reads a cue, delegates, stops | `Map` `Boundaries` | `learn` (this plugin), a research router |
| `spec` | the shape of a deliverable | `Verify` `Gotchas` | a pitch-deck or statement-of-work spec |
| `hub` | a body that is a table of contents | `References` | an index of frameworks |

**`Origin` and `Receipts` are owed by nobody.** Provenance is a frontmatter job
(`source:`, `verified:`); a section that restates a field is the ceremony this
grammar exists to delete. Write them when they carry an argument the field
cannot.

## Routing and boundary

**The description is the whole routing mechanism**, so it gets two rules rather
than one:

- **It must state a condition, not summarise the body.** 56 of 59 skills do.
  This is the loose check on purpose — a first draft demanded the phrasing `use
  this when` and scored the `naming` skill's own "when a name feels arbitrary"
  as triggerless. A narrow trigger regex produces confident false negatives,
  which is worse than a loose one; the tight call is the unscored `does-it-fire`.
- **It must state a boundary once a sibling exists.** 16 of 59 skills sit in a
  `<product>-*` (7), `<subsystem>-*` (5) or `<client>-*` (4) family, and **only 4 of those
  16** say when not to fire. That is where trigger contests come from, and it is
  the single largest real gap the rubric found.
- **The cap is 1024 characters, not 60 words.** The 60-word cap was unmeetable
  and therefore ignored: the *shortest* description in the library is 48 words
  and the median is 91, so 48 of 59 units failed a rule whose floor they were
  already near. Two units exceed 1024 characters. A cap that 81% violate is
  noise; a cap that 3% violate is a standard.

## Layout — what is already settled

Unchanged from [`CHEATSHEET.md`](CHEATSHEET.md), restated so this page is
self-contained:

```
<library>/<unit>/                 skill and routine libraries
<library>/<category>/<unit>/      template library
<library>/<category>/<unit>.md    prompt library

  SKILL.md | ROUTINE.md | TEMPLATE.md   the entry doc — required
  scripts/                              runnable
  references/                           reference-grade detail
  cron/                                 launchd plist + wrapper + scoped settings
```

Two drifts worth naming, because both are live and neither is in the checker:

- **`bin/` is not a thing.** Seven skills in the source library used `bin/` where
  the grammar says `scripts/`, including two cron harnesses. One name. (Some skills
  in this plugin still carry `bin/`; same drift.)
- **A skill is not a place to keep state.** One skill kept live `pending-*.json`
  and `sessions*.jsonl` under its own `data/`. Runtime state in a version-controlled
  unit is how a library starts merge-conflicting on its own output.

## Enforcement

| Tier | What | Where |
|---|---|---|
| **Score** | the 10 dimensions, advisory | `naming/scripts/rubric.py` |
| **Block** | identity, frontmatter, retired fields, intake shape | your naming linter (`lint`) |
| **Report** | length, staleness, index drift | same, `--tier report` |

The rubric **scores conformance, not value.** `verify-before-delete` is among
the best-argued documents in the library and scored 9/20 before migration,
because it was written before the grammar existed. A low score is a migration
distance, not a verdict on the writing.

Six dimensions are deliberately unscored, because a script that scored them
would be guessing — library fit, name quality, whether the description actually
fires, whether `source:` is true, whether a declared boundary is still true of
the sibling's body, and whether each gotcha is a real incident. `rubric.py
--review` prints them as questions.

## Gotchas

- **A whitelist of headings destroys the writing it was meant to improve.**
  Caught at N=1: the first draft of this grammar would have rewritten
  `deprecate-on-sight`'s argument headings into canon names. The canon is a
  required subset. Verified 2026-09-17 by migrating that skill and confirming
  its argument survived intact.
- **Not-applicable must score full marks.** A `judgment`-shaped unit owes no
  gate, so scoring its missing `## Verify` as 1 capped it at 19/20 and made the
  top grade unreachable by shape. Any dimension a unit legitimately cannot earn
  scores 2 with an `n/a` note.
- **A library resolver that reads a basename is broken on this machine.**
  `rubric.py` shipped with the same bug the naming linter had: it derived
  the library from the parent directory's name, and every checkout here is a
  worktree whose basename is a slug. It now walks the path for a known library
  name, then falls back to `git rev-parse --git-common-dir`. Same fix applies
  upstream — see [`enforcement.md`](enforcement.md).
- **A trigger check must be loose or it lies.** The first `TRIGGER` pattern
  required `use this when` / `whenever` and reported 13 of 59 descriptions as
  stating no trigger — including this skill's own, which opens with three
  `when` clauses. Broadened to any conditional (`when`, `before`, `after`,
  `any time`), it reports 3, and all three are real. Verified 2026-09-17.
- **A retired-spelling map must never be applied automatically.** Same class as
  naming gotcha 2. `## What the gate cannot catch` folds into `## Verify`, but
  a file holding *both* headings is exactly the file a blind rename damages.
  `rubric.py` reports the mapping and refuses to edit.

## Receipts

**Verified 2026-09-17**, against `origin/main` of all four libraries exported to
a clean tree (`git archive origin/main`), not against the working checkouts —
which are 205, 71, 9 and 11 commits behind respectively:

- `rubric.py` run over 131 units: 59 skills, 18 routines, 39 templates, 15
  prompts. Means **13.5 · 10.9 · 11.3 · 13.3** out of 20.
- The naming linter from `origin/main` run over the same tree: skills 21 block /
  61 report; routines 0/6; templates clean; prompts 0/1.
- `deprecate-on-sight` migrated to this grammar: 10/20 → **18/20**, +20 lines,
  argument headings unchanged. The last 2 points are `shape: judgment`, withheld
  until `schema.py` admits the field (phase 0c) — written today it is a block-tier
  `unknown-field`.
- The resolver fix exercised from inside a linked worktree
  (`.claude/worktrees/unit-grammar-devbox`), which is the case that fails upstream.

**Unverified**: no unit other than `deprecate-on-sight` has been migrated, so
the per-shape section profiles are proven at N=1 only. The `shape:` field is
not yet in `schema.py`, so a migrated unit currently trips `unknown-field` in
the block tier until the schema admits it.
