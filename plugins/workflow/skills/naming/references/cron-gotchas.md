# Cron-harness gotchas (naming gotchas 8–11)

Moved out of `../SKILL.md` to keep it lean. Numbering kept from `../SKILL.md` §Gotchas so
references to "gotcha 9" still resolve.

8. **A double hyphen is illegal inside an XML comment**, so documenting a CLI flag in
   a launchd `.plist` header makes the plist unparseable. Hit twice in one skill —
   `--publish`, then `--refresh-state`. Both times **`launchctl load` accepted it and
   the job ran**, so nothing surfaced; `plistlib.load()` is what catches it. Write
   flags without the leading hyphens in plist prose, and parse-check before commit:
   `python3 -c "import plistlib;plistlib.load(open('x.plist','rb'))"`.
   A tolerant loader is not a validator — this is latent breakage on reboot.
9. **A cron harness must not reference a worktree path.** Live checkouts move: a
   library's live copy can be the main checkout one month and a pinned worktree the
   next. A plist whose `ProgramArguments` points into a worktree silently stops firing
   when that worktree is re-cut. Point at an installed copy of the wrapper
   (e.g. `cp cron/<wrapper>.sh ~/"Library/Application Support/<area>/"`) or at the
   stable `~/.claude/skills/<skill>` symlink — and have the wrapper resolve the skill
   dir through a fallback list, so it fails loudly rather than half-running.
10. **A cron that writes files into a repo must own the commit.** Otherwise its
   output survives only when a human remembers, and the repo sits permanently
   dirty — which then masks real changes. Found the day a scheduled probe went
   live: it would have run four times a day forever, rewriting the same
   uncommitted report. If a cron may commit a generated file it solely owns, the
   obligation to actually commit it is the other half. Scope the commit to the exact
   path (`git commit -- reports/`) so it can never sweep up something hand-authored,
   and warn into the run log on a failed push rather than swallowing it.
11. **Shipping a plist whose wrapper does not exist fails silently, daily.** A plist
   named a `cron/*.sh` wrapper that was never written; `launchctl load` succeeds
   regardless, and the failure only shows as an empty log. If a plist names a
   wrapper, commit the wrapper in the same change, and have the wrapper write one
   heartbeat line to **stdout** — an empty launchd log is indistinguishable from a job
   that never fired.
