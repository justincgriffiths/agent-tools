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

**Default mode leaves branches open.** /wrap reviews, fixes small things, and
cards or comments the rest — it does not merge (Pitfall 1). Every open branch
stays a Blocked card naming the branch, the PR (if any), and what's gating it.

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
   the session ran under a work loop.

## 3. Update the backlog + comments for the next agent

1. Identify the board the session worked from (a `cards` table, a markdown
   kanban, an issue tracker). If the board lives in a database, write through
   a connection that can actually write to prod — a read-only MCP will fail.
2. Sync every card the session touched: status, actuals (time spent) where
   your board tracks them, links to PRs/commits.
3. Mint cards for real follow-ups discovered this session (reviewer notes
   worth acting on, deferred fixes, time-bombed TODOs like branch-blob links
   that rot after a merge). Include acceptance criteria — mandatory.
4. Leave a card comment on each card the next agent will pick up or
   needs context on: what state it's in, exact resume/unblock steps, PR URLs,
   which environment received what (staging vs prod). Write it so a fresh
   agent with zero session context can act.

## 4. Enforce: In Progress is EMPTY

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
`/archive`-style command, or keep session metrics, run it here.

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

Report, tersely: review verdict + fixes applied; artifacts written (memory /
skill / card, with gated ones marked "waiting for approval"); board delta
(cards moved, minted, commented); In Progress = empty for this session's cards
(or the named exceptions owned elsewhere); working trees clean or exceptions
named; **the handoff written** (and where), the self-review's "next time do X"
rules, and the worktree verdict as text.

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
7. **Archiving before the board is drained.** Step 5 last, always. A handoff
   written before step 4 describes cards that have since moved, which is worse
   than no handoff — the next session trusts it.
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
