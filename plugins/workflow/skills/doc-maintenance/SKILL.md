---
name: doc-maintenance
description: Weekly maintenance sweep of the OPERATIONAL docs — your main workspace repo, skill library, ~/.claude commands, loop STATE files, cron plists — for dead loops, stale paths, index drift, and failing schedulers. Stages each finding as a gated review card; never edits. Use when the user says "doc maintenance", "sweep the docs", "are the docs stale", or on a weekly schedule. Not for skill overlap/bloat (use learn audit).
argument-hint: "(no args — one bounded sweep per invocation)"
created: 2026-07-22
source: extracted from the author's working sessions, 2026 — four dead loops found rotting in docs
summary: "Weekly sweep of operational docs (workspace repo, skill library, ~/.claude commands, STATE files, LaunchAgents) for dead loops, stale paths, index drift, failing schedulers — stages gated review cards, never edits"
group: "Capture & meta"
---

# doc-maintenance — keep operational docs honest

Docs rot in a specific way here: a loop ends but its command/STATE file keeps describing it
as live; a file moves but cards and skills keep citing the old path; an index table
drifts from the directory it indexes. This skill is the recurring sweep that catches those.
Origin: 2026-07-22 — four dead loops found squatting in docs in one pass.

**Suggest-only.** Every finding becomes a gated review card (e.g. a `review/NN-*.md` file
with `approved: false`, or an issue on your own backlog). This skill NEVER edits,
deletes, or "fixes" a doc itself — the one exception is the user approving a card live and
saying "apply it".

## Boundaries (MECE with siblings)

- Knowledge-vault health (broken links, orphan pages, frontmatter) → a knowledge-base linter, not this.
- Vault shape / sync / sensitive-data sweeps → a separate vault-hygiene pass, not this.
- Skill **overlap/bloat/trigger** hygiene → `learn` Mode B, not this.
- This skill owns everything those don't: operational docs in your main workspace repo, skill library,
  template library, `~/.claude` (commands + settings-adjacent docs), loop STATE files,
  and LaunchAgent/cron liveness.

## The sweep (run all five checks)

1. **Dead loops.** Every `*STATE*.md` under your workspace's data dir and repo roots: flag files not
   marked `[CLOSED]` whose mtime is >7 days old, and any command/skill/doc describing a
   recurring loop with no matching live scheduler (LaunchAgent, cron card, or armed wakeup
   noted in the STATE). A dead loop doc reads as live work to every fresh session — that's
   the harm.
2. **Stale paths.** In `~/.claude/commands/*.md`, every `SKILL.md`, and STATE files: extract
   absolute/`~` path references and test existence on disk. Each miss is a finding (e.g. a
   card citing a spec dir that was never committed).
3. **Index drift.** The skill library's `README.md` table vs actual skill dirs;
   the template library's `MANIFEST.yml` vs template dirs; any workspace `MANIFEST.md`
   migration claims vs disk. Rows without dirs, dirs without rows.
4. **Scheduler liveness.** `launchctl list` vs `~/Library/LaunchAgents/*.plist`: loaded
   agents with nonzero last-exit (failing silently), plists present but not loaded (unless
   `.disabled`), and schedules whose runner script or log target is missing.
5. **Review-queue drift.** If your review queue is files in a repo, uncommitted files
   there (`git status`) —
   staged-but-never-committed cards are invisible to other devices and to the approval
   sweep.

## Card mechanics

Same rules as `learn` Mode B (see `${CLAUDE_PLUGIN_ROOT}/skills/learn/references/routing-rules.md`):
one card per distinct finding; before writing, check the queue for an open card on
the same doc/issue and skip if staged; never reuse a card number (next = highest existing
+ 1, deleted numbers stay dead); `approved: false` always. Findings that are pure
mechanical hygiene (e.g. "commit these 3 uncommitted review cards") may be bundled into a
single housekeeping card — don't file three cards for one `git commit`.

## Report

End with a summary: N findings, M new cards staged, K skipped-as-already-open, and the
single highest-leverage item. A clean sweep ("docs honest, schedulers healthy, indexes
true") is a valid, desirable result — say it in one line and stop.

## Pitfalls

1. **Fixing instead of filing.** A scheduled run is unattended — an edit made there ships with
   no review. File the card.
2. **Flagging history as rot.** Ledgers, pass logs, and post-mortems legitimately describe
   ended loops in past tense — only flag docs that present a dead loop as *currently live*
   (an un-CLOSED STATE header, a command inviting invocation).
3. **Re-filing weekly.** Check for an open card before staging; a suggestion the user hasn't
   approved yet is a decision pending, not a new finding.
4. **Scope creep into the knowledge corpus.** A knowledge vault's notes belong to its linter;
   touching them here double-reports.
