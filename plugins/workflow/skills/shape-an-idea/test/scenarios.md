# shape-an-idea — dry-run scenarios

Use these to test a change to the skill before you ship it. Start a fresh session, invoke
`/workflow:shape-an-idea` with the seed, and let a second person (or a second session told to
"answer as this persona, briefly, and push back once") play the idea-haver. Then score the
transcript and the idea doc against the rubric.

## Seeds

| # | Seed (what the person types) | Persona notes | What it stresses |
|---|---|---|---|
| S1 | "I want a dashboard for my team's support tickets" | The real pain is missing SLA breaches, not visibility | Trigger vs. stated idea |
| S2 | "Could we automate our weekly client report?" | Works in a repo with an existing report script | Using repo facts instead of asking |
| S3 | "An app that matches volunteers to local nonprofits" | No code yet; one key assumption, nonprofits' willingness to post, is shaky | Kill-power research, a stop or pivot outcome |
| S4 | "Help me think about pricing for my consulting offer" | Not a software idea at all | The workflow act for a non-code idea |
| S5 | "Build me a CLI that renames my photos by date" | Already fully specified | Should SKIP or shrink to a short Act 3 |

## Rubric

Score each line pass/fail. A change ships when it does not lose a pass on any seed.

| # | Check | How to tell |
|---|---|---|
| R1 | Idea doc created before the first question | Doc's first write precedes the first picker call |
| R2 | Every question carries a recommendation | Scan picker calls: first option marked recommended |
| R3 | No question asks for a lookup-able fact | Nothing like "what language is the repo?" |
| R4 | Problem statement confirmed before research | An explicit "is this the idea?" before any research sub-agent |
| R5 | Research runs in parallel | Independent sub-agents launched in one message |
| R6 | Findings carry no because-clauses | Findings section holds observations and sources only |
| R7 | Workflow ran once on a real input | The N=1 note names a real input, not a hypothetical (the checker only sees that the note exists) |
| R8 | No recommendation or verdict written for the person | No "we recommend" or "verdict" prose in the doc |
| R9 | Checker passes at close | `bin/idea-doc-check.py` exits 0 |
| R10 | S5 handled correctly | Skill skipped or went straight to a short Act 3 |

## Logging a run

Append one row per run to your own notes (not this repo) with: date, seed, skill commit, the
R-scores, and the single most surprising moment. The surprises are what drive the next edit.
