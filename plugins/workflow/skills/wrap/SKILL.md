---
name: wrap
description: >-
  End-of-session close-out ritual: /code-review everything the session touched,
  route learnings via /learn (memory / skills / templates / data), update the
  backlog, leave comments for the next agent, enforce the hard rule that
  In Progress is EMPTY at session end (every card moves back to To Do or
  forward to Blocked/Done), and finish by writing the handoff (plus a short
  self-review). TRIGGER when the user says "/wrap", "wrap up",
  "close out the session", "end of session", or an autonomous agent-loop pass
  is finishing. SKIP mid-session (that's a checkpoint, not a close-out) and for
  pure-research sessions that touched no code and no board — then only the
  /learn and handoff steps apply.
created: 2026-07-31
source: extracted from the author's working sessions, 2026
summary: "End-of-session close-out ritual: review what the session touched, route learnings via `/learn`, empty In Progress, finish with a handoff"
group: "Capture & meta"
---

# Wrap — end-of-session close-out

One command, five obligations, in order. A session is not over until all five
are done or explicitly reported as N/A. A mid-session checkpoint parks work;
/wrap closes it.

**Order is load-bearing.** Steps 1–4 change the world (fixes land, cards move);
step 5 records it. Writing the handoff first would record a state that step 4 then
invalidates.

**Default mode does not MERGE — but it does not leave drafts parked either.**
These are different things, and conflating them is what this paragraph used to
get wrong. /wrap reviews, fixes small things, and cards or comments the rest; it
does not merge (Pitfall 1). Every open branch still becomes a Blocked card naming
the branch, the PR, and what's gating it.

**A draft PR is a staging state, not a resting state (the user, 2026-09-21):**
*"draft PRs created by agents are always in an incorrect status — they need to be
worked through until they are 'ready to merge' or need to be flagged for questions
or archival."* Every PR this session opened must exit /wrap in exactly one of three
terminal states:

- **Ready for review** — draft flag removed (`gh pr ready <n>`), description
  current, checks green. It is not merged, but nothing is left for the author to
  do. This is the default target; reach for it before the other two.
- **Flagged with a question** — still a draft, but carrying a PR comment stating
  the specific decision you need from the user, and a Blocked card naming them as the
  actor. A draft with no stated question is not "flagged", it is abandoned.
- **Closed** — `gh pr close`, with a comment saying why and where the work went if
  it survives elsewhere. Superseded or exploratory work belongs here, not parked
  open forever.

**Gates (run both, do not eyeball either):**
- **Drafts:** `gh search prs --author @me --draft --state open` — any result is a
  draft still parked; a failed query is UNKNOWN, not clean. Wrap it in a small script
  whose exit code is the verdict if you run this often.
- **Ready but red:** `${CLAUDE_PLUGIN_ROOT}/skills/unstick-prs/bin/prr.sh` — every ready PR you
  authored, judged on check CONCLUSIONS: exit 0 clean, 1 a ready PR has a failed or
  cancelled check its base branch doesn't, 4 checks still running, 2/3 UNKNOWN. Run it
  on a PR (`prr.sh owner/repo#N`) BEFORE `gh pr ready`, not only at the end. A red that
  is also red on the base reads `inherited` and passes; name it in the PR comment.

A non-zero exit from either means /wrap is not finished. Verified 2026-10-05:
two PRs (an app repo and the routine library) were flipped ready with every CI job
CANCELLED (a GitHub runner outage). The draft check passed because nothing was a draft and
`receipts-check.py` passed because named checks existed; the user opened their queue and
found nothing actually ready. A cancelled check is not a green one: re-run it.

**Report PR state from the gate's output, never from memory.** A PR you opened
earlier in this same session may already be merged by the time you wrap — by you
before a compaction, or by a concurrent session (Pitfall 9, and step 1.1's
already-merged check). Verified 2026-09-21: a wrap reported two PRs as "open drafts
awaiting sign-off" that had both merged two days earlier; the claim came from
session memory while the live state was one query away.

**Merge mode is opt-in, not inferred.** Only enter it when the user's own words
in this invocation say so — "merge anything you can", "land it", "ship this",
a repo they've named as their own with no review gate. A repo having no CI or no
collaborators is not itself authorization; the instruction is. In merge mode,
step 1's touched-surface inventory becomes the merge queue: for each branch,
(a) confirm it isn't already merged (see step 1.1), (b) run the review, (c) PR
+ merge (`gh pr create` then `gh pr merge`) if it's clean and self-contained,
(d) leave it as a normal Blocked card with the specific blocker named if it
is not — a failing check, a conflicting WIP branch, a gate the repo enforces.
"Merge anything you can" means exactly that: not everything, and the leftover
half still gets a PR per step 1, not a silent skip. Sync every local checkout
whose branch just got merged with `git merge --ff-only origin/main` so the
working tree matches what shipped — an unsynced checkout is one dirty status
report away from someone assuming the merge never happened.

## 1. Code-review what the session touched

1. Inventory the touched surfaces: every repo/worktree this session wrote to
   (`git status` + `git log` since session start in each), plus PRs opened.
   **Before acting on any pushed branch — reviewing it, recommitting to it, or
   redoing its work — check whether it is already merged**: `git log
   origin/main..<branch>` (empty = merged) or `gh pr list --repo <r> --state
   merged --search "head:<branch>"`. A long session, or a concurrent one on the
   same machine, can land a branch mid-session; the branch's local worktree
   still shows it as "pushed, unmerged" until you fetch. Trust the remote, not
   your last memory of it (verified 2026-08-24: a session nearly rebuilt an
   already-merged PR's content from a stale assumption that the branch was
   still open).
2. Review the session's diff (worktree diff vs its base branch, or the PR range
   if already pushed). **`code-review` is `disable-model-invocation` — the Skill
   tool cannot call it** (verified 2026-07-28: "Skill code-review cannot be used
   with Skill tool due to disable-model-invocation"). So either do the review
   inline yourself, or tell the user to run `/code-review` if the diff warrants a
   full pass. Don't burn a turn discovering this again.
   Medium effort by default;
   if the session's lanes already passed an adversarial gate (e.g. a >300-line
   rule), this pass is a lighter regression/quality
   sweep — don't re-litigate the gate, review the FINAL state including
   post-gate fixes.
3. Findings: fix small ones now (commit + push to the open PR); card anything
   larger onto the backlog (step 3) instead of leaving it in chat.
4. **For every PR this session merged, verify its review's findings actually
   LANDED — a completed review is not a fixed finding.** Re-grep `origin/main`
   for each finding the review raised and confirm the code changed. Do not
   accept the review notification as evidence; it reports what was *found*, and
   says nothing about what was *fixed*.

   The failure this exists to catch: a review that finishes while the PR is
   still open, reports N findings, and gets read — by the user, and by the
   session that ran it — as a discharged obligation. They then merge, which is
   the correct action on the signal they have. Findings and fixes are
   indistinguishable at merge time and only one of them changes the code.
   Verified 2026-09-03: an app PR's review returned four real findings
   including a NULL-COGS cascade that would fail the ENTIRE dbt build for every
   client; the PR merged two days later with all four live, and they sat in
   `main` for a week until this step caught them (fixed in a follow-up PR).

   A finding against an already-merged PR does not evaporate — it is now a
   finding against `main` and needs its own branch, per the default no-merge
   rule above. Fix findings; don't just report them.

## 2. Route learnings (/learn Mode A) + update routines

1. Invoke the `learn` skill routing tree over the session: project memory /
   global CLAUDE.md (confirm first) / skill / backlog card. Most sessions
   yield 0–2 durable artifacts — a quiet step is fine.
2. Beyond memories, patch the OPERATIONAL surfaces the session proved stale —
   this is the step people skip:
   - lane/loop prompts and STATE protocol sections (e.g. a wrong repo path a
     lane prompt shipped with),
   - skills whose assumptions broke (fix directly only if trivial + owned;
     otherwise stage a card per learn Mode B),
   - templates/data files the session revealed gaps in (seed formats, config
     scaffolds).
3. Update the loop ledger/STATE file for the pass (est vs actual, gotchas) if
   the session ran under an agent loop.

## 3. Update the backlog + comments for the next agent

**Prefer GitHub over a separate card board.** Every follow-up becomes an **issue** — or a
**PR** when the fix is code — in the repo that owns the work (the app repo for the app, the ops
repo for scripts and notes, the skill/routine libraries for harness tooling). If you still keep
a card board, the same rules apply to its cards.

1. Identify the repo(s) the session's follow-ups belong to. If the session ran under a
   loop that still reads a kanban (markdown project files, a loop board), sync that too.
2. Sync every issue and PR the session touched: state, labels, links to commits.
3. Open one issue per real follow-up discovered this session (reviewer notes worth
   acting on, deferred fixes, time-bombed TODOs like branch-blob links that rot after a
   merge). Body: where it stands, what's needed (who does which step), **done means** —
   acceptance criteria are mandatory. Labels from the repo: `lane:*`, a gate label for a
   decision only the user can make, `P0`–`P3`, `bug`. Use
   `gh issue create --body-file -` with a heredoc. If a guard hook refuses commands
   containing certain phrases (e.g. "force-push"), one such body can take down a whole
   batch: write "rewrite shared history" instead, and create issues one or two per command
   so a single refusal does not take the batch down.
4. Leave a comment on each issue or PR the next agent will pick up or needs context on:
   what state it's in, exact resume/unblock steps, PR URLs, which environment received
   what (staging vs prod). Write it so a fresh agent with zero session context can act.

## 4. Enforce: In Progress is EMPTY

Applies to any kanban the session actually used (on GitHub the equivalent is that every
issue this session worked carries a state comment and no unfinished one is left assigned to
a dead session).

Hard rule (user, 2026-07-22): at session end, the In Progress column contains
NOTHING owned by this session. For each such card, exactly one move:

- **→ To Do**: not meaningfully started, or started-then-abandoned — with a
  comment on what exists (worktree path, partial branch) so work isn't redone.
- **→ Blocked**: work done or paused on an EXTERNAL dependency — name the
  blocker in a comment (e.g. "PR #N awaiting merge", "needs the user's OAuth").
- **→ Done**: shipped and verified per its acceptance criteria.

Cards in In Progress owned by OTHER live sessions/lanes are not yours to move
— list them in the wrap report instead.

## 5. Write the handoff (archive the session)

LAST, once steps 1–4 have settled, write the durable handoff a fresh session boots
from, plus a short self-review ("next time, do X"). Optional: if you have an
`/archive`-style command, or keep session metrics, run it here — and if it records what
the session shipped, write that sentence yourself (one concrete line naming the artifact
and its state; "nothing durable" is a real answer). Never ask the user to score a session
from memory: put the session's numbers in the question, offer one-click options, and
record the sentence even when they don't answer.

Two deconflictions with the steps above — get these wrong and you either
duplicate work or contradict a hard rule:

1. **Memories are already done.** Step 2 routed learnings
   through the `learn` tree, which owns memory placement and scope. Do NOT
   re-derive or re-write memories in the archive pass — verify step 2's
   artifacts exist and move on. If the archive pass surfaces a genuinely new
   durable fact, route it through the learn tree rather than writing it
   straight to the memory dir.
2. **Worktree teardown is a RECOMMENDATION only.** If the archive pass
   emits a teardown verdict, /wrap never acts on it (see Pitfall 5). Carry the
   verdict into the report
   as text. Never remove the worktree hosting this session, regardless of what
   the verdict says.

The handoff must reflect the FINAL state — post-review-fixes, post-board-sync,
post-In-Progress-drain — including which environment received what (staging vs
prod) and any gate still pending. Write it for an agent with zero session
context.

## Verification (the wrap report)

Report, tersely: **the draft check's and `prr.sh`'s results and what they listed** (a non-zero exit is a
blocker, not a footnote — name each draft and which of the three terminal states
you moved it to); review verdict + fixes applied; artifacts written (memory /
skill / issue, with gated ones marked "waiting for approval"); backlog delta
(issues opened, commented, closed; PRs opened) with their URLs; In Progress = empty for this session's cards
(or the named exceptions owned elsewhere); working trees clean or exceptions
named; **the handoff written** (and where), the self-review's "next time do X"
rules, and the worktree verdict as text.

**Optional: an independent second-model check of the status word (shadow).** Line 1 of the
report is its status word. If you have a judge model wired up — `JUDGE_CMD` set to a command
that answers the JSON protocol documented at the top of `bin/wrap_verdict.py` — check the
claim against the user's asks instead of only self-grading it. Without `JUDGE_CMD` the
pipeline exits 3 (advisory) and changes nothing; omit line 2 then. Before you emit the report:

1. **Draft the whole report to a temp file** (`draft="$(mktemp "${TMPDIR:-/tmp}/wrap-report.XXXXXX")"`)
   whose **line 1 is your claim**: `DONE`, `PARTIAL`, `BLOCKED` or `FAILED`.
2. **Run `${CLAUDE_PLUGIN_ROOT}/skills/wrap/bin/wrap_status.sh "$draft"`.** It finds this
   session's transcript from `$CLAUDE_CODE_SESSION_ID`, runs
   `wrap_evidence.py | wrap_verdict.py --report "$draft"`, prints the verdict JSON,
   and saves the same bytes to `~/.local/state/wrap/<session_id>.json`.
3. **Emit the report with line 2 set by the exit code:**
   - **0 or 1**: `Judge: <computed> (<consistent|overclaim>) — <reasons>; unsure: <unsure>`
     (0 = consistent, 1 = overclaim; `reasons` and `unsure` come from the JSON,
     `none` when empty).
   - **3**: `Judge verdict unavailable: <advisory>` (or omit line 2 when no judge is
     configured at all).
   - **2**: no verdict. Report it in the wrap report as a bug, with the script's
     stderr. Do not hand-build the pipeline instead.
4. **Line 1 stays your claim** unless all three hold: `WRAP_VERDICT_MODE=live`,
   exit 1, and `computed` is `PARTIAL` or `BLOCKED`. Only then does line 1 become the
   computed word. Never write `DONE`, `UNCLEAR`, `n/a` or `null` into line 1, and
   never replace it on exit 0 or 3. **The default is shadow** (unset means shadow):
   the verdict sits beside the claim and changes nothing. Promote to live only after
   the judge has earned it — e.g. ≥20 sessions the user labelled, ≥90% agreement, and no
   disagreement on a downgrade — as a separate, deliberate step.

| step | primitive | question + options | state source | mode | risk |
|---|---|---|---|---|---|
| wrap:verdict | `yes_no` + `choice` + `score`, one batch | per ask: a request? superseded? how far (delivered-verified / delivered-unverified / partial / not-started / narrowed); plus unverified_claim, lands_on_user, claimed_j, completeness | `wrap_evidence.py`: the user's asks from the transcript, git/gh facts, files written; plus the draft report | shadow | downgrade only; a key-shaped state is refused (exit 2); no judge or judge down = exit 3, claim unchanged |

## Pitfalls

1. **Merging during wrap.** The default is: wrap closes the session, it does
   not merge — if a merge gate (adversarial review, user sign-off) is
   pending, the card goes to Blocked with the gate named, not to Done. Merge
   mode (see above) is the sole, explicit exception — enter it only when
   the user's invocation says so, never by inference from "this looks safe".
2. **Comments that only make sense with session context.** The next agent
   has none. Paths, PR URLs, env names, exact commands.
3. **Claiming gated artifacts are live.** Backlog cards and CLAUDE.md edits are
   proposals until approved.
4. **Board writes on the wrong pipe.** A read-only database connection against
   prod fails the write; use one that can write.
5. **Worktree teardown.** Wrap does NOT remove worktrees — worktree removal is
   a destructive op with its own rules.
6. **Skipping step 2's "patch the routines" half.** A stale lane prompt that
   burned 10 minutes this session burns 10 minutes every session until the
   prompt/template itself is fixed — the memory alone doesn't fix the prompt.
7. **Archiving before the backlog is synced.** Step 5 last, always. A handoff
   written before steps 3–4 describes issues and cards that have since moved, which
   is worse than no handoff — the next session trusts it.
8. **Double-writing memories.** Step 2 owns memory placement; the archive pass
   must not re-derive it. Two passes writing the same fact to different scopes
   is how the memory dir rots.
9. **Redoing work a branch already shipped.** A branch you pushed earlier in
   this same session can be merged by the time you get to wrap — by you, in a
   part of the conversation now summarized past a compaction boundary, or by
   a concurrent session on the same machine. `git status` on a stale local worktree cannot
   tell you this; only `git fetch` + a check against `origin/main` can.
   Verified 2026-08-24: rebuilding a routine believed missing overwrote one
   that had shipped hours earlier, and separately, an already-merged skill PR
   was nearly redone from scratch. Fetch and check before you build, not after.
