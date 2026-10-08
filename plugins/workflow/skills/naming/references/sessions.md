# Background sessions — the status prefix

Detail behind the fourth grammar in `SKILL.md` §2. Units are invoked, records are
sorted, branches are places work happens, and **a background session is a row in a
list somebody scans to decide what to keep**. That is the only grammar in the house
whose reader is making a lifecycle decision, so it is the only one whose name carries
lifecycle.

```
[STATUS_][NNN_]TAG_slug      YOU_014_BLD_copy-accuracy-audit   DEL_BAU_rsvp-and-block-time
                             AGT_044_SOP_slim-learn-routing    055_BLD_q4-media-plan
```

| Slot | Answers | Set | Changes? |
|---|---|---|---|
| `STATUS` | whose move is next: `YOU` the user's, `AGT` an agent's, `DEL` nobody's | at wrap and on every sweep | **yes, re-read each time** |
| `NNN` | did this session claim a durable thread? | once, when named | never |
| `TAG` | what kind of work | once | never |
| `slug` | which job, never which client | once | never |

## Why the status exists — a prediction is not an observation

The grammar was `[DEL_][NNN_]TAG_slug` until 2026-09-29, and the number was meant to
separate threads the user carries from one-offs they can close. **Verified 2026-09-29**
against the session list and its registry:

- **Inflation**: 51 of 57 sessions carried a number. A session that has just done a lot of
  work almost always predicts that it matters, so the numbered block was the whole list.
- **No exit**: 53 of 56 registry rows were open. Nothing moved a thread out except a
  tombstone, and 2 sessions had ever been tombstoned.
- **Frozen names**: a name records the work as it looked at the start. A `032_RTN_…`
  name for a cleanup job said nothing, 11 days later, about whether the cleanup was done.

The number is a **prediction** made once. The status is an **observation** made each
sweep. The keep-or-delete decision turns on the observation, so the observation had to
go in the name, and something had to re-read it. That is `SKILL.md` principle 7.

**Considered and kept:**

- **The number stays.** The alternative was to replace it with the status. Keeping it
  means a thread's number still resolves its registry row and survives a status change.
- **The client ban stays for session slugs.** The alternative was to lead the slug with
  the client. It was kept, even though a few live slugs already broke it and the ban leaves
  several client sessions that cannot be told apart by client.

## Choosing the status

- **Branch pushed, no PR**: `AGT`. An agent opens the PR.
- **PR open**: `YOU`. The user reviews and merges.
- **Session state `blocked`**: `YOU`. The session is waiting on an answer inside it.
- **Drafted send**: `YOU`. An email, message or ticket nobody sent is theirs to send.
- **Nothing open anywhere**: `DEL`. Name the evidence in the reason (the merged PR, the
  issue that now carries the item), so the promise is checkable.
- **Idle under a day, or still working**: no status. Its next move is probably its own.

The reason is not implied. Store it beside the session (a small sidecar file that is
deleted with the session works) and show it next to the name in any audit listing. Write
it for someone deciding from that one line: name the branch, PR, draft or decision.

## One slug, one thread

**Verified 2026-09-29:** three jobs each held two numbers. Two mechanisms, both worth
refusing in whatever names your sessions:

- **Re-mint on re-run.** Re-naming an already-numbered session allocated a second
  number. Re-running should keep the number and only retag the row.
- **Mint instead of rejoin.** A new session continuing a job minted a fresh number.
  The namer should refuse a slug another row owns and name the thread, so the session
  rejoins it (reopening a closed row if need be).

The consequence under the client ban: the same job for a **second client** collides on
slug. Decide which it is. The same thread continuing → rejoin. A different job that
happens to share a shape → a slug that names what differs in the *job* (`offer-test-brief`
vs `creative-test-brief`), never the client. Pre-existing duplicates can be grandfathered:
only a slug *change* collides.

## Parse order — every status is tag-shaped

`DEL`, `YOU` and `AGT` are three capitals followed by `_`, exactly the shape of a tag. Any
checker that tests tags first reads `YOU_014_BLD_x` as tag `YOU`, loses the number, and
"repairs" the rest. **Every parser strips the status first** — the namer, any audit, and
any reaper that reads the registry number. **Verified 2026-09-29** by fixture: before the
fix, a reaper resolved no registry row for `YOU_014_…`. `SKILL.md` gotcha 12 states the
general rule.

## Where enforcement lives

Not in the library naming linter. That checker sees library units and records, and no
session name ever reaches it. A workable split:

- **Grammar and renames**: a small session-naming script (`status`, `del`, `rejoin`, `audit`).
- **Evidence**: a read-only reaper that reports what each session left open. It never writes.
- **Backstop**: a prompt hook that nudges when the current session is unnamed.
- **Front door**: a rename command that names a session and sets its status at wrap.
- **Sweep judgment**: a session-cleanup skill that reads the reaper's evidence.
