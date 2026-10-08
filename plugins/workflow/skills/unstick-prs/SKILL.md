---
name: unstick-prs
description: Judgment for pushing a stuck PR to a decidable state — fixed, rebased, verified, flipped ready, or honestly closed — without merging or deploying anything. Fire for "unstick PRs", "sweep stuck PRs", "why is this PR stuck", "get the drafts ready for review", and inside a scheduled PR-sweep run. NOT for merging/promoting (your repo-specific ship steps), NOT for building new features.
intake:
  verbs: [sweep, report]
  required: []
  optional: [repos, window]
created: 2026-08-18
source: extracted from the author's working sessions, 2026 — ~20 finished drafts found stranded; 13 dispositioned in one sweep (10 ready, 2 closed-superseded, 1 triaged)
summary: "A caught PR is a bug: the disposition tree, safety envelope, and verified gotchas for unsticking PRs, interactively or overnight"
group: "Capture & meta"
first-run: 2026-08-18 — the manual 13-PR sweep this skill encodes (several library repos, an app repo and a site repo)
---

# unstick-prs

Push a stuck PR to a state the user can act on in one glance. Never merge, never
deploy — the sweep's whole output is a cleaner approval queue, not shipped code.

Optional: run it nightly from a scheduler that starts a headless session with this skill
loaded; keep the receipt comment, digest and triage comment as fixed templates so every run
reads the same.

## The stance: a caught PR is a bug

Stuck work is a process defect, not a backlog item. Fix it fully — rebase, rebuild,
fold, close, root-cause its CI — don't be precious. Exactly two exclusions:

1. **Actively being worked on.** Updated in the last ~2h, or its author-session is
   visibly mid-flight (sibling commits landing on related branches — verified
   2026-08-18: a templates-repo PR appeared mid-sweep while its session was still
   pushing generator fixes; touching it would have collided). Skip and name it in
   the digest.
2. **Created and shared by someone external** — not the user, not this machine's
   sessions, not an agent we dispatched. Other-authored PRs are read-only: never
   flip, never push, never close (e.g. a consent-gated scaffold marked "do not
   merge" stays exactly as its author left it). Report-only.

## What "stuck" means

Open + own-authored + any of: **draft** · **ready with failing checks** ·
**CONFLICTING** — and not excluded above. Drafts are the core case: the user's review
queue only sees ready-for-review, so a finished draft is invisible work.

## Disposition tree (per PR, in order)

1. **Re-verify state at act time** (`gh pr view`) — never trust the enumeration
   snapshot; PRs merge/close under you mid-sweep.
2. **Read body + full diff; run `gh pr checks`.** Diagnose every red check: caused
   by this PR → fix it; pre-existing on the base branch → root-cause it in its OWN
   PR (opened ready), then carry that branch into the blocked PR so it goes green
   now and its diff collapses when the fix merges.
3. **Fix in isolation.** Clone/checkout the PR branch under the job tmp dir — never
   in the user's working copies. Push back to the same branch;
   `--force-with-lease` only, and only onto the PR's own branch.
4. **Disposition** — exactly one of:
   - **ready** — verified finished (checks green or failure documented as
     inherited, referenced paths resolve, repo conventions met) → tighten the body
     to match reality, `gh pr ready`, receipt comment.
   - **close-superseded** — a successor exists → **fold first, then close**: merge
     the superseded content into the successor so nothing is lost, then close with
     a comment naming the successor and the fold commit.
   - **draft-intentional** — genuinely unfinished and out of sweep scope → honest
     triage comment (what exists, what's missing, whose decision blocks it); stays
     draft. Flipping it would be dishonest about state.
   - **untouched** — excluded (mid-flight / external) → one line in the digest.
5. **Receipt comment — mandatory on every touched PR.** What was stuck, what the
   sweep did, what the user needs to consider — in a fixed format, so receipts
   read the same every night. A fix without the comment is
   invisible work — the exact bug this skill exists to kill.

## Safety envelope (hard rules)

- Never `gh pr merge`. Never push to main/staging/any canonical branch. Merges,
  promotions, and deploys are the user's, always.
- Repo-specific ship steps belong to their owners: per-repo ship skills, and any
  auto-promote / staging-gate jobs that already own a repo's forward motion — never
  duplicate them.
- Force-push: `--force-with-lease` onto the PR's own branch only, and only when
  the branch is being rebuilt/rebased — never onto a branch another session moved
  (the lease failing IS the mid-flight detector firing late; stop).
- Report outcomes faithfully: a verification that didn't actually run is worse
  than none (see receipts — the vacuous-verification trap). If the sweep must
  leave something broken, the digest says so plainly.

## Boundaries (MECE with siblings)

- **Building new work from the backlog** — out of scope. This never builds; it
  readies what a build left behind.
- **Repo ship skills** — own staging/prod motion on their repos. This
  skill stops at "ready to merge".
- **doc-maintenance** — docs and schedulers, stage-only. Different surface, and
  its suggest-only rule does NOT apply here: a scheduled run of this skill acts on
  PR branches by design (it may push to a PR's own branch, never merge).

Gotchas with receipts: [`references/receipts.md`](references/receipts.md) — read
it before the first fix of a sweep; every entry is a confident wrong turn that
already happened.
