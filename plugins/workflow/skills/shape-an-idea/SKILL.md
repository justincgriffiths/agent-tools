---
name: shape-an-idea
description: Turn an idea that is clearly worth doing, but not yet specified, into a spec cheaper agents can execute. One session, part interview and part coding, ending with deliverables, a timeline and work packages sized for a model tier, one of them proven by handing it to that tier. Use for "spec this out", "break this into work for the agents", "shape this idea", "turn this issue into delegable work", "/shape-an-idea", or any issue that says what and why but leaves how, in what pieces and by whom open. Owns the line between facts (the agent finds them) and decisions (the person makes them), the bar a spec must clear (a cheaper agent can run it without asking a question), and the autopilot mode in which an agent shapes an idea alone and stops only at gates. SKIP for raw notions with no evidence they matter (talk first), for work already split into packages a mid-tier agent can run (just dispatch them), and for stress-testing a finished plan (a grilling skill).
argument-hint: "the idea or an issue reference (repo#n); add 'autopilot' to let the agent answer its own questions and stop only at gates"
intake:
  required: [idea]
  optional: [issue, mode, audience, deadline, constraints, where-to-save]
created: 2026-10-12
source: extracted from the author's working sessions, 2026. Ideas that were useful enough to file but stayed parked because nobody broke them into pieces a cheaper agent could pick up, and specs that read clearly to the author but sent a smaller model in the wrong direction.
summary: "Shape a worthwhile but unspecified idea into deliverables, a timeline and tiered work packages, and prove one package on a cheaper agent"
group: "Capture & meta"
---

# shape-an-idea

The ideas that stall are the ones in the middle of the backlog. Each is useful enough to file,
with a clear what and why, but nobody has turned it into pieces someone else can pick up. A
frontier model can usually work out the how on the fly, but it is too expensive to spend on
every chunk of work. A cheaper model needs the how written down. This skill writes it down,
in a session that is fast and engaging enough that the person wants to stay in it.

**The bar:** a spec is done when **a cheaper agent can execute each work package without
asking a question**. Clear to the author doesn't count, and neither does complete-looking.
The skill proves the bar by handing a package to that agent (Act 4).

**The failure this prevents:** a parent issue with "child to open" in four places that stays
parked for weeks. Or the opposite: the work gets dispatched anyway, and a small model
confidently builds the wrong thing from a spec only its author could read.

---

## The one rule

> **Facts are the agent's job. Decisions are the person's.**

Never ask for something you could look up, such as what the repo holds, what a tool returns,
or what the data says. Dispatch a sub-agent and keep the conversation moving. Never decide the
business logic yourself: who it is for, thresholds, money, scope cuts, what "good" means. Put
each one to the person as a question, with your recommendation attached.

Autopilot (below) moves this line, but it doesn't erase it.

---

## Modes

| Mode | Who answers the questions | Stops for the person at |
|---|---|---|
| **Interactive** (default) | The person, from your recommendations | Every round |
| **Autopilot** | The agent, from evidence and recorded precedent | Gates only, then one final review |

**Gates are always the person's, in every mode:** who it is for, money (budgets, prices,
spend), anything client-facing or outward-facing, anything irreversible, and any decision you
would make with low confidence.

In autopilot, log every self-answered decision as `agent (assumed)` with its evidence and
confidence. At the end, put the whole log to the person in one review round: accept all, or
pick the ones to revisit. **Count the overturns** and record the rate in the doc. A low
overturn rate across several sessions is the evidence for widening autopilot; one session
proves nothing.

---

## The artifact: one idea doc

Create it **before the first question**, so the person can watch it fill in.

- **Where:** `docs/ideas/<slug>.md` in the current repo, unless the person names a place. When
  shaping an issue, link the doc from the issue.
- **Shape:** copy [`references/idea-doc.md`](references/idea-doc.md). Each section starts as
  `_pending_`.
- **Check:** `python3 ${CLAUDE_PLUGIN_ROOT}/skills/shape-an-idea/bin/idea-doc-check.py docs/ideas/<slug>.md`
  exits 0 only when the doc clears the bar. Run it before calling the session finished.

Write each decision into the doc the moment it's made. If the session dies halfway, the doc
should still be worth handing on.

---

## Act 0 — Intake: what's already settled

When the idea arrives as an issue, read it to the end, with its comments, linked issues, and
anything it says was "ruled" or "decided". Write each settled point into the decision log as
`carried`, with its source. **Don't re-ask what the issue already settled.** Re-asking a
decision the person already made is the fastest way to lose them.

Look for **siblings**: open issues that share a deliverable with this one, such as two reports
that both need the same token-to-dollars step. Name them in round one. A shared deliverable is
built once and serves both issues.

---

## Act 1 — Shape (interview)

Goal: a problem statement the person would sign, and the decisions that bound the work.

Map the open questions as a **decision tree**, and work it in **rounds**:

1. **Ask the frontier, all at once.** The frontier is every open decision whose prerequisites
   are settled. Use the native question picker, up to four questions per call.
2. **Recommend on every question.** Put your recommended answer first and mark it. Each
   option says what it does to the work, e.g. "adds a backfill package" or "drops the weekly
   cadence".
3. **Never ask downstream of an open question.** It waits for the next round.
4. **Recompute after every answer.**

Ask **one devil's-advocate question** per session, usually in round two: "What is the
strongest case for not doing this at all?" Ideas that survive it get better specs, and ideas
that don't survive it were never going to be cheap.

**Stop when** you can show a problem statement and the person answers yes to "is this the
idea?" Two or three rounds is typical. Past five rounds, the idea is really two ideas: say so,
and ask which one to shape.

---

## Act 2 — Research (plan, then launch)

Goal: every assumption the spec depends on, labelled **known** (with a source) or
**unknown**.

1. **List the assumptions** under each decision. Rank them by **kill-power**: if this one is
   false, does the idea die, or does only a detail change?
2. **Write one research question per high-kill assumption.** Give each a method (repo read,
   web search, tool query, spike), a done-when condition and a timebox. See
   [`references/research-plan.md`](references/research-plan.md).
3. **Launch them in parallel**, in one message, after the person cuts or adds questions in one
   picker round. Keep interviewing on the branches the research doesn't touch.
4. **Report findings as observations with sources.** What a finding means for the idea is the
   person's call: keep going, change direction, or stop.

A spike counts as research. When the risky assumption is "the API returns X", fifteen minutes
of code against the API settles it. Keep spikes in a scratch directory.

---

## Act 3 — Break down: deliverables, packages, timeline

Goal: work that can be handed out. See
[`references/work-packages.md`](references/work-packages.md) for the field rules and the tier
table.

1. **Deliverables** are what the person tracks: three to six outcomes, written in concrete
   nouns, each with a done-means the person could check without reading code.
2. **Work packages** are what agents execute. Write one or more per deliverable, and keep each
   to **one fire, one reviewable outcome**. Every package carries: goal, inputs (exact paths,
   tables, endpoints), output, acceptance (a check that passes or fails), a do-not-touch list,
   depends-on, **tier**, and estimated human-minutes.
3. **Tier each package at the cheapest rung that will succeed.** If a package needs a frontier
   model only because the spec is vague, the spec is the defect: tighten the spec, then
   re-tier. Anything that needs a gate decision is tiered `human`.
4. **Timeline:** order the packages by dependency, mark the critical path, and convert the
   minutes into dates using the person's real capacity. Ask for that capacity; never assume
   full-time.

Show the package table and timeline in one message, then take cuts and changes in one picker
round.

---

## Act 4 — Dry-fire: prove the spec

Pick the package **most likely to be misread**. Usually that is the cheapest-tier package
doing the most consequential work. Hand it to a sub-agent **on its assigned tier**, with only
the package text and none of this conversation:

```
Before doing anything, list every question you would need answered to do this well.
Then do it, in <scratch dir> only, and report against the acceptance check.
```

- **The agent asked questions, or missed acceptance:** the spec has a defect. Fix the package,
  and fix any sibling package with the same gap. Re-fire, at most twice.
- **It passed with no questions:** record it. The tier is proven for this kind of package.
- **It still fails after two fixes:** move the package up one tier and write down why. That
  becomes a calibration point for the next session.

Record the outcome in the doc: package, tier, questions asked, pass/fail and what changed.
This is the receipt that the spec meets the bar.

---

## Act 5 — Publish (with the person's go-ahead)

Creating issues is outward-facing, so confirm before writing them. Then write one parent issue
for the person to track, plus one child issue per package, using the house work-item grammar
(`write-work-items`, if installed) and tier labels the dispatcher understands. Link the idea
doc from the parent. If the source was an existing issue, that issue becomes the parent: edit
it, don't duplicate it.

---

## Making it engaging

What keeps a person in the session is fast, visible progress where every answer changes
something:

- **Readiness meter.** End every round with one line, e.g.
  `Readiness ▓▓▓░░░ 3/6 · 9 decided · 2 unknown · next: research`. The six steps are problem,
  decisions, research, packages, timeline and dry-fire.
- **Short turns.** One round or one finding per message. Picker answers take a click, not a
  paragraph.
- **Show the consequence.** When an answer adds or drops a package, say so in the next line:
  "That drops the backfill package, 2 h saved."
- **Let them jump.** If they want to go straight to packages, let them. Unanswered questions
  stay visible as unknowns, and the meter shows the gap.
- **Name detours.** Anything over about 15 minutes gets offered as a trade, not quietly taken.

---

## Closing the session

The session is finished when all four of these are true:

- **Bar met:** `idea-doc-check.py` exits 0, and the dry-fire passed or the package was
  re-tiered with a reason.
- **Person confirmed:** they confirmed the problem statement and approved the packages. In
  autopilot, they also reviewed the decision log.
- **Published or parked:** the issues are written, or the person chose not to publish and the
  doc says so.
- **Pointer given:** the final message links the doc and the parent issue, and gives the
  autopilot overturn rate if that mode ran.

Don't write a recommendation or verdict on whether to do the work. The doc holds the
decisions and findings; the "should we" paragraph belongs to the person.

---

## Gotchas

- **Settled-looking isn't specified.** An issue with a plan and four "child to open" lines is
  right in this skill's band. Carry the decisions it settled, then shape the rest.
- **Agreeable answers are not decisions.** "Sure" on your recommendation is weak evidence. On
  the decisions that bound the work, ask for the reason in the person's own words.
- **Research sprawl.** Only high-kill assumptions get a sub-agent. Everything else stays in
  the doc as an open question.
- **Silent tools lie.** A connector that returns nothing may be disconnected. Make one call
  that must return something before you report "nothing exists".
- **A frontier tier hiding a vague spec.** If you reach for the top tier, ask what a smaller
  model would get wrong, and write that answer into the package.
- **Dry-firing the easy package.** It proves nothing. Fire the package you're least sure of.
- **Autopilot creep.** Gates never become `agent (assumed)`, however obvious the answer looks.

---

Interview technique (design tree, frontier rounds, recommendation on every question) adapted
from [mattpocock/skills](https://github.com/mattpocock/skills) `grilling` (MIT). Complexity in
estimated human-minutes follows METR's time-horizon work.
