# Enforcement — why it is generated, and where it is thin

Moved out of `../SKILL.md` §5 to keep it lean.

## Why generate rather than document

**The index drift is the argument for generating rather than documenting.** The skill
library's `README.md` had six skills missing under a CLAUDE.md rule that said to update the
index in the same commit as any skill change. The rule was prose, so it lost. Nothing was
generated, so nothing noticed. A prose-only rule is a draft.

## Where the enforcement is genuinely thin — design for these up front

- **Worktrees break basename-based library detection.** A linter that derives library
  identity from the **basename** of the path it is given fails in a git worktree, because
  `git rev-parse --show-toplevel` returns the worktree path (`.../worktrees/<slug>`), not the
  library name. If the hook then treats any non-zero exit as a violation *while discarding
  stderr*, it blocks every commit with an empty reason — and if every checkout is a
  worktree, that is 100% of commits. **Verified 2026-08-21:** installed on a skill library,
  the hook blocked a test commit from a worktree with a blank finding list; removed again.

  Two fixes, both needed:
  1. The linter resolves the library by walking the path for the deepest component that
     names a known library, not by basename. That fixes every worktree layout.
  2. The hook distinguishes exit 1 (violations — block) from exit **2** (lint could not
     run — warn and allow). Fail-closed with no message is worse than no gate.

  **Unverified:** that both fixes together make the hook safe on a worktree-based
  checkout. They were later confirmed by reading the code only; re-install the hook and
  make a test commit from a worktree before relying on it. Until then the weekly digest is
  the only live backstop.

- **An installer that skips linked worktrees** (`[ ! -d "$lib/.git" ]` — in a worktree `.git`
  is a file) reads as "worktrees are unprotected", but hooks live in the **common** git dir, so
  installing on the main checkout covers every worktree. The skip is misleading, not protective.
- **Hooks are per-clone and untracked**, so a fresh clone silently has no block tier. Have the
  report tier list unhooked clones.
- **`--no-verify` exists.** The digest should still surface what was bypassed — bypassing
  should cost a line in a report, not silence.
- **The report tier proposes and never applies.** It cannot fix a stale skill; it can only
  make sure you know.
