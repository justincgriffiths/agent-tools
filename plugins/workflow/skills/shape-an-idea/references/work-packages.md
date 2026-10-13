# Work packages — fields, tiers, timeline

The mechanics for Act 3. The judgment is in SKILL.md.

## Tiers

Size each package in **estimated human-minutes** (how long a competent person would take),
then pick the cheapest tier whose one-pass horizon covers it. The horizons follow METR's
time-horizon findings, set conservatively: a model reliably finishes tasks of about a third
of its 50%-success horizon. **Edit the "Runs on" column for your own stack.**

| Tier | Runs on (example) | One-pass horizon | Use for |
|---|---|---|---|
| `script` | No model; a deterministic script | n/a | Fully mechanical: same input gives the same output, zero judgment |
| `small` | Haiku-class | ≤ ~20 min | Extraction, formatting, config edits, single-file mechanical changes |
| `mid` | Sonnet-class | ≤ ~120 min | Routine feature work with explicit acceptance criteria |
| `frontier` | Opus-class or above | ≤ ~240 min | Novel design, multi-repo changes, deep debugging |
| `human` | The person | n/a | Gate decisions, credentials, irreversible or outward-facing steps, validation |

**Over horizon?** Split the package. **Tiered `frontier` because the spec is fuzzy?** Fix the
spec instead. **Overran 2× at its tier?** Promote it one tier next time, and note why.

## Package fields

Every field is required. A blank field is a question the executing agent will have to guess.

| Field | Write it as | Bad | Good |
|---|---|---|---|
| Goal | One sentence, outcome-first | "Work on pricing" | "Every session row carries an estimated USD cost" |
| Inputs | Exact paths, tables, endpoints, issue refs | "the metrics data" | "`data/sessions/*.jsonl`, fields `model`, `tokens_*`" |
| Output | The artifact and where it lands | "a table" | "`prices.yaml` + a `usd_est` column, PR to `main`" |
| Acceptance | A check that passes or fails | "looks right" | "September total within 5% of the Anthropic line on the card statement" |
| Do-not-touch | Files, systems or decisions out of bounds | (blank) | "Don't change the attribution rule; don't write to prod" |
| Depends-on | Package IDs | (blank) | "P1, P2" |
| Tier | One of the five above | "Opus probably" | `mid` |
| Est. min | Human-minutes | "a few hours" | `90` |

## Package table (in the idea doc)

```
| ID | Deliverable | Goal | Tier | Est. min | Depends-on | Acceptance |
|---|---|---|---|---|---|---|
| P1 | D1 | ... | small | 20 | – | ... |
```

Full field detail (inputs, output, do-not-touch) goes in a `### P1` block under the table. The
table is for scanning; the blocks are what gets published as child issues.

## Timeline

1. **Order by dependency** and mark the critical path (the longest dependent chain, in
   minutes).
2. **Ask for capacity.** How many agent runs a day, and how many minutes the person can give
   to `human` packages each week. Never assume full-time.
3. **Convert to dates.** Agent packages are limited by runs per day plus review time. Human
   packages are limited by the person's weekly minutes. Put review time in explicitly: every
   agent output needs a person or a gate to accept it.
4. **Show it as a table** (package, start, end, owner), not as prose.

```
| Week of | Packages | Owner | Gate |
|---|---|---|---|
| 10-19 | P1, P2 | agent (small) | – |
| 10-19 | P3 | person | decide price table source |
```

## Dry-fire brief

Hand the agent only the package block. Don't include the idea doc, this conversation, or
your notes, because the executor won't have them either.

```
<package block: goal, inputs, output, acceptance, do-not-touch>

Before doing anything, list every question you would need answered to do this well.
Then do it, in <scratch dir> only, and report: questions asked, what you did,
acceptance pass/fail with evidence.
```

Every question it asks points at a field that needs fixing. Fix the field in the package, and
look for the same gap in the sibling packages.
