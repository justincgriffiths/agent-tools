# learn

Break a session into its reusable parts and send each one to the place that will actually use it. Also audits your skill library for overlap and bloat.

## When to use it

- **End of a session**: you built something with a second use and want it kept, not just remembered.
- **Mid-session failure**: a tool or skill turned out to be wrong, and the session holding the evidence should fix it now.
- **Skill library cleanup**: you suspect your skills overlap, are bloated, or never fire.

Not for wiring a hook itself. The skill hands that to `update-config`.

## How to use it

```
/workflow:learn            # capture this session's learnings
/workflow:learn audit      # sweep the skill library
```

In plain words: *"capture learnings"*, *"break this down into reusable parts"*, or *"are my skills overlapping?"*

**Capture mode** then:

1. Lists what the session built or settled, one line each, instead of summarizing what was learned.
2. Checks whether an existing skill covered the work and failed to fire. That is a trigger defect.
3. Routes each element, in order, to the first store that fits: hook, template, routine, prompt, skill, team knowledge base, repo `CLAUDE.md`, global `CLAUDE.md`, a GitHub issue, and project memory last.
4. Writes the artifacts, loads any skill it just wrote, and checks each one would have caught the failure it came from.
5. Reports one line per artifact and marks which claims are verified and which are not.

**Audit mode** then:

1. Inventories the skill library.
2. Checks for overlap, bloat, broken frontmatter, near-duplicates, stale provenance, oversized descriptions, unverified claims, and skills that did not fire.
3. Opens one GitHub issue per new finding, skipping ones already open.

## Example

A session that built a deck, a render command, and found a tool bug yields a template, a routine, and a hook request. It does not yield one note called "what happened in the session."

## What you get

- Capture mode: new or edited files in the stores above. Anything gated (a global `CLAUDE.md` edit, an issue) is reported as waiting for approval.
- Audit mode: GitHub issues proposing changes. It never edits or deletes a skill on its own.
- Quiet runs are normal. A session with nothing durable produces nothing.

## Scripts

Run from the skill folder.

```
scripts/scan-skills.sh [skill-library-dir]
```
Prints one row per skill: name, line count, resource dirs, first words of the description. Default directory is `$SKILL_LIBRARY`, else `~/.claude/skills`.

```
scripts/scan-skills.sh | scripts/overlap-judge.py
```
Optional second-model check for overlapping skills. Log-only, always exits 0. Needs `JUDGE_CMD` and `JUDGE_REDACT`; without either it does nothing. `JUDGE_LOG` sets the log path.

```
scripts/hookrefs.sh [library-dir]
```
Lists hook paths that skills cite but that are missing, not executable, or not wired in settings. Exit 0 clean, 1 findings, 2 error.

## Requirements

- **CLIs**: `bash`, `gh` (audit issues), `python3`, `jq` (for `hookrefs.sh`).
- **Env vars** (optional): `SKILL_LIBRARY`, `JUDGE_CMD`, `JUDGE_REDACT`, `JUDGE_LOG`.
- **MCP connectors**: none.
