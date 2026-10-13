<!--
Idea doc template for shape-an-idea. Copy to docs/ideas/<slug>.md before the first question.
Every section starts as _pending_ and is replaced when its act closes.
bin/idea-doc-check.py checks this shape. Keep the seven ## headings exactly as written.
-->
# <Idea name>

_Started <YYYY-MM-DD> · mode: interactive | autopilot · source: <issue ref or "conversation">_

Readiness ░░░░░░ 0/6

## Problem statement

_pending_

<!-- One or two sentences the person signed off on. Who has the problem, what it costs today,
what changes when it's solved. -->

## Decision log

| # | Decision | Chosen | Decided by | Round |
|---|---|---|---|---|
| D1 | _pending_ | _pending_ | _pending_ | _pending_ |

<!-- One row per decision, written the moment it is made.
Decided by: the person's name · "carried (<source>)" for a decision settled before the session
· "agent (fact)" for something looked up · "agent (assumed, conf: high/med/low)" for an
autopilot answer. The checker needs at least one row decided by the person.
Autopilot: add a line "Overturned: N of M" after the person's review. -->

## Assumptions

| # | Assumption | Kill-power | Status |
|---|---|---|---|
| A1 | _pending_ | _pending_ | _pending_ |

<!-- Kill-power: high / med / low. Status: unknown / known / waived.
"waived" = the person chose to proceed without knowing; the risk stays named here. -->

## Research

_pending_

<!-- One block per research question:
### R1 — <question> (tests A1)
- Method: repo read | web search | tool query | spike
- Done when: <condition> · Timebox: <minutes>
- Finding: <observation> — source: <link/path> — confidence: high/med/low
-->

## Deliverables and timeline

_pending_

<!-- Deliverables table: ID | deliverable | done-means (checkable without reading code).
Then the timeline table: week of | packages | owner | gate. Then one line naming the
critical path and the capacity assumption the person gave. -->

## Work packages

_pending_

<!-- Package table, then one ### block per package. See references/work-packages.md.
| ID | Deliverable | Goal | Tier | Est. min | Depends-on | Acceptance |
Tier is one of: script, small, mid, frontier, human. -->

## Dry-fire

_pending_

<!-- Package fired · tier · questions the agent asked · what changed in the spec · re-fires.
End with a line "Result: pass" or "Result: re-tiered to <tier> because <reason>". -->
