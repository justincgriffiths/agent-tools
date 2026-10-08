---
name: write-work-items
description: Write work items at two levels for two audiences — parent cards the user tracks (what changed for the business, why, done-means) and child requests agents execute (technical brief, verify-first, don't-touch). Use BEFORE queueing work to an agent loop, minting a set of backlog cards, or handing a backlog to any agent; and whenever a list of tasks "means very little" to a human reviewer or hides how few real things it actually is. NOT for speccing a single card in depth; this one sets the levels across a SET.
created: 2026-08-01
source: extracted from the author's working sessions, 2026 — a task list that 'meant very little' to a human reviewer
summary: "Write work items at two levels for two audiences — parent cards the user tracks, child requests agents execute"
group: "Capture & meta"
---

# write-work-items

A list of tasks that a human can't scan is not a backlog, it's a transcript. The fix isn't
shorter tasks — it's **two surfaces**, because there are two readers and they need opposite things.

| Surface | Reader | Contains | Never contains |
|---|---|---|---|
| **Parent card** (epic) | the user | **What we're doing** (the actual changes, in concrete nouns), why it matters in risk/money terms, done-means, rolled-up child status | File paths, line numbers, commands, "append the block from X" |
| **Child request** | the agent that executes it | Exact brief: what to change, what to verify FIRST, what NOT to touch, what done looks like | Business rationale, strategy, anything requiring a decision |

Mixing them is the defect. A parent full of implementation detail can't be scanned; a child
full of rationale invites the agent to redesign the task.

**The parent's hardest section is "What we're doing" — and there are two ways to blow it.**
Too low is a transcript ("append the universal block to line 240 of app-repo/CLAUDE.md").
Too high is a slogan that says nothing: "stop the rules from lying," "improve estate hygiene."
Both fail the same test — *they still don't know what you're about to change.* The level that
works names the real thing in plain nouns: **"Delete the GSD-workflow mandate from the app
and infra repos' CLAUDE.md — that tooling was removed in May, so the command they order agents to
run doesn't exist."** Repo names, real artifacts, the actual edit, the reason it's wrong. No
paths, no line numbers, no commands. If your bullet could describe five different tasks, it's a
slogan; if it can only be executed by opening a specific file, it's a transcript.

## Procedure

1. **List the items you were about to write.** Don't write them yet.
2. **Find the 2-4 real things.** Group by *shared cause or shared outcome*, not by repo or file
   type. If you can't name the group in one sentence a non-engineer would nod at, it isn't a
   parent yet. Ten items collapsing to three parents is the normal ratio; if nothing collapses,
   suspect you're writing transcript.
3. **Write each parent**: title in plain words · **what we're doing** (one bullet per real
   change, concrete nouns, child id in parens — see the level test above) · why-it-matters
   (name the risk or the gain in their terms — money, data loss, wasted hours, client-facing) ·
   done-means (a state they can check in 60 seconds).
4. **Write each child** to the granularity rule: **one fire, one reviewable outcome.**
   - Too small: "append a block to a file" — batch those into one child per repo.
   - Right: "the portal has a CLAUDE.md that states its RLS invariant."
   - Too big: needs a mid-flight decision, or spans repos → split, or gate it to the human.
5. **Stamp provenance on every item**: `source:` (the call, audit, card, or person that caused
   it) and `why:` (one line). **If you can't write the `why`, the item isn't ready to queue** —
   that test alone kills most self-referential busywork.
6. **Gate anything expensive**: merges, deploys, prod, secrets, or where a wrong guess costs
   more than asking. Gated items are the human's queue, not the agent's.
7. **Re-read the parent list as the user.** Three to five lines, each one obviously worth doing?
   Ship it. Still opaque? You grouped by mechanics instead of outcome — regroup.

## Smell tests

- **Self-referential queue**: every item traces to the session that invented it, none to a
  client, a call, or a card. The loop is grooming itself. Point it at the real backlog.
- **The `why` column repeats the title** — the item has no rationale, only a description.
- **A parent you could hand to an agent verbatim** — it's a child wearing a parent's hat.
- **A parent with no "what we're doing"** — outcomes and rationale only. Right length, wrong
  level: they can't tell what you're about to change. (The user, 2026-08-01: "now you're not
  actually saying what you're doing.")
- **Same verb across 8 items** ("append the block to…") — that's one parent, one child per repo.

## Where this shows up

- A file-based agent queue — e.g. a `_TEMPLATE.md` carrying the child format + granularity
  rule, an `_epics/` dir holding the parents, and a script that prints the rolled-up parent view.
- Cards on a backlog board — same split: epic card vs. agent-runnable child cards.
- Deep-speccing ONE approved child (PRD + tech spec) is a separate job. This skill decides
  what the children *are* and what the parent says.

## Origin

2026-08-01. Nineteen agent-queue cards, every one technically correct, that the user read as
"those tasks mean very little to me" — and they were right: they were three things (lying rules ·
one rule set everywhere · measure-then-run-unattended) wearing nineteen hats. The cards were
written for the agent and shown to the human.
