# naming

Decide what to call a thing, and where it lives, before you create it. A house grammar for a
library of agent skills and their siblings: routines, templates, prompts, branches, sessions.

## When to use it

- **Before authoring**: you are about to add a skill, routine, template, prompt, directory or script.
- **Before a branch or worktree**: you are about to run `git checkout -b` or `git worktree add`.
- **Before a batch rename**: including a sweep of a list of background sessions.
- **Name clashes**: a name feels arbitrary, or two things want the same name.
- **New frontmatter**: you are about to invent a field. The skill says to check the schema first.

Not a linter. The skill carries the judgment. Enforcement belongs in a linter you own.

## How to use it

```
/workflow:naming
/workflow:naming audit
/workflow:naming audit --library <library>
```

`audit` is the only argument the skill documents. It runs the vocabulary check and hands you
the candidates. `--library` narrows the scan; without it, all four libraries are read. You can
also ask in plain words, e.g. *"what should I call this new skill?"* or *"which library does this belong in?"*

The skill then answers three questions in order:

1. **Which library owns it**: skills, routines, templates or prompts, using a one-line test for each.
2. **What it is called**: kebab-case for units, a separate grammar for records, branches,
   worktrees and background sessions.
3. **How it is invoked**: the argument grammar, and what to do when a required slot is missing (ask, never assume).

In `audit` mode it proposes vocabulary rulings and you decide. It never renames anything.

## Example

You want a skill that tightens marketing copy. The skill suggests naming the job, not the
domain: `tighten-copy`, not `copy-style-system`. No client name, no `-v2`, `created:` and
`source:` in the frontmatter, and a `skills/` home because the value is judgment, not a fixed command sequence.

## What you get

A recommended library, name and invocation shape for the thing you are creating, in chat.
In `audit` mode, a list of same-concept naming candidates to rule on. The skill does not
edit files, rename anything or write a glossary row for you.

## Reference files

In `references/`:

- **`CHEATSHEET.md`**: one-page lookup of the grammar.
- **`invocation.md`**: the argument grammar in full.
- **`asking.md`**: how a unit asks for a missing slot.
- **`vocabulary.md`**: one concept, one word.
- **`unit-grammar.md`**: the body and shape of a unit.
- **`rubric.md`**: scoring a unit against the grammar.
- **`records.md`**: names for rows in a set (campaigns, ads, media files).
- **`branches.md`**: branch and worktree names, with a device tag.
- **`sessions.md`**: background session names.
- **`field-rulings.md`**: why each invented frontmatter field was kept or retired.
- **`enforcement.md`**: linter, generator and hook design, and where it is thin.
- **`cron-gotchas.md`**: gotchas for scheduled harnesses.
- **`receipts.md`**: what was verified, and how.

## Scripts

`scripts/rubric.py` scores a unit against the rubric. Ten mechanical dimensions, 0 to 2 each,
20 points. Judgment dimensions are printed as review prompts, not scored.

```
python3 scripts/rubric.py <library-or-unit> [...] [--min N] [--kind skills|routines|templates|prompts] [-v] [--review] [--print-table]
```

- **`--min N`**: exit 1 if any unit scores below N (default 16).
- **`--kind`**: force the library kind when it cannot be inferred from the path.
- **`-v`, `--review`**: per-unit detail and the judgment prompts.
- **`--print-table`**: print the scoring table and exit.

Exit codes: 0 all units at or above the minimum, 1 at least one below, 2 the tool could not run.

## Requirements

`python3`. The script uses only the standard library. No credentials, no connectors.
