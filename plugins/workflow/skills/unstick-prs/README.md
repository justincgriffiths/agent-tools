# unstick-prs

Push each stuck pull request to a state you can act on in one glance: fixed, rebased,
verified, flipped ready, or honestly closed. It never merges and never deploys.

## When to use it

- **Stranded drafts**: finished work is sitting in draft, invisible to your review queue.
- **Red or conflicted PRs**: ready PRs with failing checks, or merge conflicts.
- **A nightly sweep**: run it inside a scheduled headless session so the queue stays clean.
- **"Why is this PR stuck?"**: you want a diagnosis and a disposition.

Not for merging or promoting (use your repo's ship steps) and not for building new features.

## How to use it

```
/workflow:unstick-prs
```

The SKILL.md declares the verbs `sweep` and `report` and the optional slots `repos` and
`window`, but does not give a flag syntax. Say what you want in plain words, e.g. *"unstick my
PRs"*, *"why is this PR stuck?"* or *"get the drafts ready for review."*

The skill then works each of your open PRs in order:

1. Re-checks the PR's current state, then reads its body and diff and runs `gh pr checks`.
2. Diagnoses every red check. If this PR caused it, it fixes it. If the base branch is already
   red, it root-causes that in its own PR.
3. Fixes in an isolated checkout, never your working copy. Pushes to the PR's own branch only, with `--force-with-lease`.
4. Picks exactly one disposition: **ready**, **close-superseded** (fold the content into the
   successor first), **draft-intentional** (leave a triage comment) or **untouched**.
5. Leaves a receipt comment on every PR it touched.

It skips PRs updated in the last couple of hours, and PRs written by someone else (report only).

## Example

A draft PR is finished but its rebase is stale. The skill rebases it, runs the checks gate,
confirms no check is red or cancelled, tightens the body to match what was verified, flips it
ready and comments with what it did.

## What you get

- **Ready PRs**: drafts that pass the gates, flipped ready with a receipt comment.
- **Closed PRs**: superseded ones, closed with a comment naming the successor.
- **Triage comments**: on PRs that stay draft, saying what exists, what is missing and who decides.
- **A digest**: untouched PRs get one line each.

It will not run `gh pr merge`, push to a main or staging branch, or touch another author's PR.

## Scripts

In `bin/`. Run them directly if you want to check a PR yourself.

**`prr.sh`** lists ready PRs whose CI is red or pending, ignoring checks also red on the base branch.

```
prr.sh                 # every open, ready PR you authored
prr.sh owner/repo#123  # just these PRs
```

Exit 0 none red or pending, 1 red, 2 query failed, 3 unparseable response, 4 none red but some
pending. Treat 2, 3 and 4 as unknown, not green. It appends to `prr.log` beside the script.

**`receipts-check.py`** is the gate before flipping a PR ready. It exits 1 if the PR has zero
named checks.

```
gh pr checks <n> --json name,state,bucket | python3 receipts-check.py --body <body-file>
python3 receipts-check.py --checks <file> --body <body-file>
```

Exit 0 at least one named check, 1 none, 2 usage error. `--body -` reads the body from stdin.
`--pr <n>` only labels the PR number on the optional second-model log row (`JUDGE_LOG`).

**`prr.py`** is the filter `prr.sh` uses. It reads check rollups as JSON on stdin.

## Requirements

- **`gh`**: authenticated, with access to the repos.
- **`git`** and **`python3`**.
- **`JUDGE_CMD`** (optional): a command for the log-only receipts judge. Unset skips it. Also
  `JUDGE_REDACT` (redactor filter) and `JUDGE_LOG` (log path override).
