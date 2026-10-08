# Hygiene heuristics — the Mode B checks

Run against the output of `scripts/scan-skills.sh`. Judge only **user-authored** skills — the
ones symlinked from your skill library (plus any local authored dirs). Skip vendored /
official skills (Cloudflare: `cloudflare*`, `agents-sdk`, `durable-objects`, `sandbox-sdk`,
`wrangler`, `workers-best-practices`, `turnstile-spin`; Anthropic official carry
`license: Complete terms in LICENSE.txt` — e.g. `skill-creator`, `frontend-design`, `web-perf`,
`canvas-design`, `claude-api`, `doc-coauthoring`, `web-artifacts-builder`). You don't own those;
a card proposing to edit them is noise.

Each finding becomes ONE card. A "finding" is a distinct, fixable problem — not every whiff.
Prefer precision over volume: a library that gets five vague cards a week trains the user to
ignore the queue.

## 1. Overlap / MECE violation (highest value)

Two or more descriptions competing for the same trigger phrases, so a plausible user prompt
matches several. Symptoms:
- The same distinctive noun/keyword list appears verbatim in multiple descriptions, with only a
  weak verb distinguishing them (the classic: N skills split by *verb* but advertising the same
  *nouns*).
- One skill's description is a **superset** of another's scope ("anything X" that swallows a
  narrower sibling).
- Two skills disambiguated only by a path/repo the user often won't say out loud.

**Card:** name the colliding skills, quote the overlapping phrase, and propose the concrete fix —
usually a description retune (lead with the discriminator, drop the shared generic phrase), or a
consolidation (merge N verb-split skills into one with internal dispatch + `references/`).

Optional: a second-model check — `scan-skills.sh | scripts/overlap-judge.py` pairs skills that
share distinctive description words and asks a judge model (`JUDGE_CMD`) whether each pair
competes for triggers. Log-only and advisory; it skips cleanly when no judge is configured.

## 2. Bloat

`SKILL.md` over ~300 lines. Big bodies load slowly and bury the operative steps. **Card:** propose
moving the reference-grade detail into `references/<topic>.md` loaded on demand, leaving a lean
SKILL.md that points to it. Note the current line count and roughly what should move.

## 3. Broken / missing frontmatter

No YAML block, or missing `name:` / `description:`. Such a "skill" can't register or trigger
reliably. **Card:** propose the exact frontmatter to add (a real `name:` and a pushy MECE
`description:` inferred from the body).

## 4. Near-duplicate purpose

Two skills that do substantially the same job (beyond mere trigger overlap). **Card:** propose
merging, or sharpening each one's scope so they're genuinely distinct.

## 5. Missing or stale provenance

Library skills must carry `created:` (yyyy-mm-dd) and `source:` in frontmatter. **Card** when
either is missing, or when `created:` is older than ~6 months — a staleness check, not an
automatic delete: propose re-validating the skill against how the work is actually done now.

## 6. Oversized description

`description:` over ~60 words. Long descriptions drift into other skills' trigger space and slow
recognition. Existing skills are grandfathered — **card only** when the length co-occurs with a
real overlap risk (a shared distinctive phrase with another skill), and propose the tightened
wording. New skills should start ≤60 words.

## 7. Unverified assertion (correctness, not form)

Checks 1–6 are all about *shape* — overlap, size, frontmatter. None of them notice that a skill is
confidently **wrong**. This one does.

Flag a skill that states tool or system behavior with no evidence it was ever exercised:

- A specific claim about how a tool responds ("returns success even when it fails", "silently
  truncates", "errors on multiple matches") with no `**Verified <date>:**` marker and no
  `**Unverified:**` label.
- A procedural step that presupposes such behavior ("search first to check whether X exists" —
  which is wrong if that search is semantic and can't answer existence).
- Guidance whose provenance (`source:`) is a session that plainly could not have exercised it —
  e.g. a claim about a failure mode in a skill `created:` before that failure was ever seen.

**Why it matters more than bloat:** an inferred gotcha is worse than a missing one. It sends the
next agent down a confident wrong diagnostic path. Real case, 2026-07-28: a Notion-writing skill shipped
with "a non-matching `old_str` is a no-op, not an error." Three tests later it errors loudly every
time — and the *real* bug (silently dropped `properties`) was a different mechanism entirely. Every
form-based check above passed that skill.

**Card:** quote the claim, say what would exercise it, and propose either running that test or
labelling it `**Unverified:**`. Prefer retract-in-place over deletion — a silently removed wrong
claim teaches nothing and gets re-derived.

## 8. Trigger miss (a skill existed and didn't fire)

Evidence that a skill was present and registered, but work squarely inside its scope happened
without it being invoked. Signals:

- A session transcript doing a skill's job by hand (grep session history for the skill's own
  distinctive commands or file paths appearing outside any invocation of it).
- A skill created mid-session, then not used for the remainder of that same session.
- The user asking for something in words that plainly match a skill's domain but not its
  `description` vocabulary.

This is the check that catches the failure the whole library is built to prevent: a correct skill
that never loads is worth nothing. Real case, 2026-07-28 — a Notion-writing skill was written, registered,
and then not loaded, and the session went on to hit two failures the skill already documented.

**Card:** name the skill, quote the work that bypassed it, and propose the concrete description
retune (add the trigger phrasing the user actually used). If the miss is structural rather than
lexical — the skill can't fire because nothing prompts a lookup — propose a **hook** instead and
hand off to `update-config`.

## What NOT to card

- Style nits, wording preferences, or anything that isn't a triggering/correctness/context cost.
- Vendored/official skills (see the skip list above).
- A finding already staged in an open card this run — query open cards first and skip it,
  so a scheduled run doesn't re-file the same suggestion.
- A skill that's simply short — small is good, not a defect.
