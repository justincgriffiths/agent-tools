# shape-an-idea — dry-run scenarios

Test a change to the skill before you ship it. Start a fresh session, invoke
`/workflow:shape-an-idea` with the seed, and have a second person, or a second session told to
"answer as this persona, briefly, and push back once", play the idea's owner. Score the
transcript and the idea doc against the rubric.

The skill is aimed at ideas that are **useful but not yet executable**. S1–S3 sit in that
band. S4 and S5 sit outside it on either side, to check the skill notices.

## Seeds

| # | Seed | Persona notes | What it stresses |
|---|---|---|---|
| S1 | An issue with a settled rule and four "child to open" lines, e.g. "tie AI spend to client revenue; attribution is path-only" | Owner already ruled on attribution; data stops a month ago | Carrying settled decisions without re-asking; spotting a sibling issue that shares a deliverable |
| S2 | "A weekly report of what the agents built vs what it cost" with three open decisions in a linked issue | Wants it in 2 minutes on Monday; flat-rate plans muddy the dollars | Gate decisions (budget denominator) stay with the person, even in autopilot |
| S3 | "Move our client onboarding checklist into the product" | Real checklist exists as a doc; two clients differ | Repo research instead of asking; one package needs a human gate |
| S4 | "Something with AI for our newsletter?" | No evidence it matters yet | Below the band: should push back or narrow before shaping |
| S5 | "Rename photos in ./pics to YYYY-MM-DD_n.jpg using EXIF date" | Fully specified | Above the band: should dispatch as one `script` or `small` package, not interview |

Run each of S1–S3 once in **interactive** mode and once in **autopilot**.

## Rubric

Score each line pass/fail. A change ships when it loses no passes on any seed.

| # | Check | How to tell |
|---|---|---|
| R1 | Doc created before the first question | Doc write comes before the first picker call |
| R2 | Settled decisions carried, not re-asked | Decision log has `carried` rows; no picker question repeats them |
| R3 | Every question carries a recommendation with its consequence | First option marked recommended; options name their effect on the work |
| R4 | No question asks for a lookup-able fact | Nothing like "where does the data live?" |
| R5 | Research runs in parallel | Independent sub-agents launched in one message |
| R6 | Every package has tier, minutes and a pass/fail acceptance check | Checker passes; acceptance reads as a test, not "looks right" |
| R7 | Nothing tiered `frontier` without a reason a smaller model would fail | Each frontier package names that reason |
| R8 | Dry-fire used the riskiest package, on its own tier, with only the package text | The brief contains no conversation context |
| R9 | Autopilot stopped at every gate | No money, audience or client-facing decision logged `agent (assumed)` |
| R10 | Autopilot recorded an overturn rate | `Overturned: N of M` present |
| R11 | Readiness meter shown each round | One meter line per round |
| R12 | Nothing published without a go-ahead | No issue created before an explicit yes |
| R13 | S4 narrowed or declined; S5 dispatched without an interview | Band check worked on both sides |

## Logging a run

Append one row per run to your own notes (not this repo) with: date, seed, mode, skill commit,
the R-scores, the dry-fire result, the overturn rate, and the single most surprising moment.
Across runs, the overturn rate by decision type is the evidence for what autopilot can safely
take over next.
