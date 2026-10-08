# Receipts — verified

The unverified item (a weekly report job on a real schedule) stays in `../SKILL.md` §Receipts.

**Verified 2026-08-17:** a linter, index generator, normalizer, and the generate-tier apply
(dry run and apply) were run against four libraries; the finding counts in this skill are
measured, not estimated.

**Verified 2026-08-21** (during a scheduled-probe build, which is where gotchas 8–10 and the
block-tier finding come from): hook install then removal on a skill library; a worktree
commit blocked with an empty finding list and allowed again after removal; the linter
exiting 2 on a worktree basename; `plistlib.load()` rejecting a plist that `launchctl load`
had accepted and run; a launchd job firing on `launchctl start` and writing its heartbeat to
both logs.
