# One concept, one word

The rest of this skill governs the **form** of a name: kebab-case, which library owns
it, which frontmatter fields are legal, how it is invoked. All of that can be wrong
while every individual name is impeccable — because form says nothing about whether
two well-formed names mean the same thing.

That is the gap this page fills, and it is the gap the skill already admits to:

> *Judgment:* whether the name says what the thing is. `app-page` and `app-home`
> both pass the checker; whether they are one skill is your call.

**The rule: a concept gets one word, and that word is written down.** A second word for
a concept you already named is not a style problem. It is a retrieval problem — a
reader or an agent searches the right idea with the wrong string, gets nothing, and
concludes the thing does not exist. That is how a library grows a second
implementation of something it already had.

Precedent, both directions: a knowledge-base taxonomy that collapsed 36 drifting page
types into a 5-type vocabulary, and a status-vocabulary rule that fixes the meaning of
DONE / BLOCKED / PARTIAL / FAILED. Its governing line is this
page's thesis: *"They are not stylistic choices and they are not interchangeable. If a
report needs a word not defined here, define it here first."*

## Where the vocabulary lives

A `glossary.yml` beside your naming linter. One row per concept: the canonical word,
the variants that are not it, the surfaces the rule applies to, and the authority the
ruling rests on.

A row there is not documentation. It is a **check** — a vocabulary checker (`vocab.py`) reads the glossary and
greps the controlled surfaces, so an accepted ruling immediately starts enforcing
itself. That is the whole point of writing the audit down rather than remembering it:
a prose-only rule is a draft.

## What is checked, and what is deliberately not

Only **controlled surfaces**: unit and script names, intake verbs and slots, headings,
enum values. Never prose.

This restriction is doing real work, and the size of the gap is the argument. Measured
2026-09-18 across four live libraries:

```
# prose: 868 occurrences
grep -roIE --include='*.md' --include='*.py' --include='*.sh' --include='*.yml' \
  -i '\bcheck\b' <worktrees>/*/live | wc -l
# controlled surfaces: 5  (terms.py: a term extractor over headings, names, slots)
terms.py <worktrees>/*/live | awk -F'\t' 'tolower($2) ~ /(^| )check( |$)/'
```

868 against 5. Almost all of the prose is ordinary English — "check the output", "a
quick check" — and none of it is drift. A **heading** called "Checks" in a library
whose canonical word for that section is "gates" is drift, because a heading is a
structural slot with a fixed role, and two words in one slot is ambiguity a reader
has to resolve. Counting prose would bury the five real hits under 863 false ones.

The surface is the evidence. Without it the signal drowns: prose-level counting says
all twelve inspect-verbs are in heavy use, which is true and tells you nothing.

## Adjudicating a candidate

A clustering step (`cluster.py`) proposes pairs. It cannot decide, and it does not try — it deliberately
suggests no canonical, because the obvious heuristic (take the more-used word) is wrong
often enough to be dangerous. On an early run it proposed retiring `when to use` in
favour of `when to skip`. Frequency measures habit, not correctness.

Work a candidate in this order and stop at the first that answers:

1. **Is it one of the four false-positive classes?** Then it is not a candidate:
   - **Opposites** — `when to use` / `when to skip`. Guarded automatically.
   - **Role suffixes** — `created` / `created_by`. A date and a person. Guarded.
   - **Different scopes** — the same word, two vocabularies. `procedure` looks like a
     variant of `routine`, but a knowledge-base taxonomy declares `procedure-` as
     one of its five canonical filename types, so the word is load-bearing there. The
     glossary therefore **excludes it from `variants` entirely** rather than scoping a
     rule around it: a rule that fires on a word another vocabulary owns is a rule that
     gets switched off. Expect zero `procedure` findings — that is correct.
   - **Genuine distinctions wearing similar clothes** — `lint` is mechanical, `triage` is
     ordering by urgency, `verify` is confirming a claim you already made. Three words,
     three jobs.
2. **Does the house already have an answer?** Then you are not deciding, you are
   recording. §1 of this skill says the routine library owns fixed steps, so `routine` beats
   `runbook` and `playbook` without further argument. Cite the authority in the row.
3. **Is there a clear majority shape?** Then name it. **Inventory before you
   legislate:** write down what the tree already does — counts, not impressions — then
   name the majority shape as the rule.
4. **Otherwise, do not rule.** Leave it `state: proposed` with the question written out.
   An honest open question costs a line in the register. A guessed ruling becomes a
   check, and a wrong check is worse than none — it will be enforced on files that were
   already right.

**Severity follows the surface, not the strength of your opinion.** Machine-facing
surfaces — unit, verb, slot, script — are `block`, because a wrong word there breaks
invocation or search. Human-facing surfaces — heading, enum — are `report`, because a
wrong word there costs a reader a second, not a run.

## The one thing this must not become

A rename campaign. The register **proposes and never applies**, like every other
report-tier output here. The first run found 51 occurrences (2026-09-18); whatever the
count is when you read it, it is a map, not that many edits due this week. Most rows should be fixed when their file is next opened for another
reason, and the glossary is what makes sure the question is not re-litigated in the
meantime.

A rejection is worth recording as much as an acceptance. Write it into the concept's
`note:` with the reason — that is what stops the audit proposing it again every week,
and it is the difference between a register that converges and one that nags.

## Scope against `learn`

`learn` Mode B audits skill **descriptions competing for the same trigger** — two units
whose distinctive nouns overlap so the router cannot choose. This page audits **one
concept named differently across units**. Adjacent, not identical. `learn` files GitHub
issues; this files a glossary register, so there is no channel collision — but if a finding
is really "these two skills are the same skill", it belongs to `learn`, not here.
