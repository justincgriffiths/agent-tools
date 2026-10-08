# Routing rules — per-store format

Read this before writing to any store. It carries the exact mechanics so `SKILL.md` stays lean.

> **Section order is historical, not priority order.** The routing tree in SKILL.md is the
> authority on *which* store, and it evaluates the acting stores (hook → template → routine →
> prompt → skill) before the informing ones, with memory **last**. Section 1 below is the last
> resort, not the first choice.

## 1. CC project memory (`~/.claude/projects/<encoded-cwd>/memory/`) — LAST RESORT

The encoded cwd is the working directory with slashes turned to dashes — e.g. `~/myproject` →
`-Users-<you>-myproject`. One fact per file. Frontmatter + body, per `~/.claude/CLAUDE.md`:

```markdown
---
name: <short-kebab-case-slug>
description: <one-line summary — used for relevance during recall>
metadata:
  type: user | feedback | project | reference
---

<the fact. For feedback/project, add **Why:** and **How to apply:** lines. Link related
memories with [[their-slug]].>
```

- `user` — who the user is (role, expertise, preference).
- `feedback` — guidance on how to work (a correction or a confirmed approach); include the why.
- `project` — ongoing work / goals / constraints not derivable from the code or git history;
  convert relative dates to absolute.
- `reference` — a pointer to an external resource (URL, dashboard, ticket).

Then add ONE line to that project's `MEMORY.md` index: `- [Title](file.md) — hook`.
Before saving, check for an existing file that already covers it and update that instead of
duplicating. Don't save what the repo already records (structure, past fixes, git history,
CLAUDE.md). Declarative phrasing — memory is re-read as fact, so "The user prefers X", never
"Always do X" (that reads as a standing directive later).

## 2. `~/.claude/CLAUDE.md` (global, every project)

Only for a standing directive that must apply everywhere. **Confirm with the user before
editing** — it's always-on and affects every Claude Code session. Keep additions short and in
the existing voice. If the behavior is automated ("whenever X happens…"), it belongs in a hook
via the `update-config` skill, not here.

## 3. A hook (`~/.claude/hooks/` + `settings.json`)

For a **mechanical guard** — "tool Y silently drops Z", "never call W without doing V first".
Hand off to the `update-config` skill; it owns `settings.json` and carries the full hook contract.
The essentials:

- Script in `~/.claude/hooks/<name>.sh`, `#!/usr/bin/env bash`, `set -euo pipefail`, `chmod +x`.
- stdin is JSON: `{session_id, tool_name, tool_input, tool_response}` (`tool_response` is
  PostToolUse only). **Pass the event as an argv arg** rather than inferring it from the payload.
- **Advisory output:** emit
  `{"hookSpecificOutput": {"hookEventName": "<event>", "additionalContext": "<text>"}}`. That text
  is injected into the model's context. Prefer this over blocking — a blocking hook on a common
  tool is worse than the bug it guards.
- `matcher` is a string pattern and **works with full MCP tool names**
  (`mcp__claude_ai_Notion__notion-update-page`) — **Verified 2026-07-28.**
- **Merge, never replace** the event's array — other hooks live there.
- Degrade silently: exit 0 on empty or malformed stdin, so a guard can never break a tool call.
- **Pipe-test before wiring**, then `jq -e` the settings nesting, then trigger the real tool once to
  prove it fires. A hook that silently does nothing is worse than no hook.

## 3b. A template (your template library)

One kebab-case dir under a plural category (e.g. `webpages|pitches|contracts|analyses|reports|dashboards`),
carrying a `TEMPLATE.md` whose frontmatter is mandatory and complete: `name` (matches the dir),
`category`, `formats`, `source`, `created`, `brand`, `placeholders`, `status`. Body = when to
use it and how to fill it.

**Update `MANIFEST.yml` and the README index in the SAME commit** as any add/remove/rename —
this is the repo's own hard rule and drift here is a known recurring defect.

- **Edit here, never in a consumer mirror.** A mirror synced into a consumer repo is overwritten
  by the next sync; edits made there are destroyed silently. Before any sync, scan
  for drift you would clobber: `${CLAUDE_PLUGIN_ROOT}/skills/dedupe/scripts/scan-tree.sh --canonical
  <templates-repo> --vendored <consumer-mirror> --name templates`.
- **Placeholder syntax is per-family, do not migrate working systems.** `{{PLACEHOLDER}}` for
  HTML/web/email; `[Token.Name]` + `[[signature]]`/`[[date]]` for contracts.
- **Strip client PII** to generic example data (`dana@acme.com`, `Starlight LLC`). Named clients
  only as deliberate case-study content, never as leftover fill-in values.

## 3c. A routine (your routine library)

One kebab-case dir: `ROUTINE.md` + executable scripts (`chmod +x`, `set -euo pipefail`, paths as
arguments, nothing hardcoded).

**The two bars that decide whether it belongs here at all:**
1. **It is a script, not prose.** If an agent must re-derive the commands from a description, it
   is a skill. Do not file prose here.
2. **It ends in a verify gate.** No artifact without a check that the artifact is correct. No
   gate ⇒ `status: draft`, and say so.

State plainly in `ROUTINE.md` what the gate *cannot* catch and what a human must eyeball —
structural checks are necessary, not sufficient. Scripts degrade gracefully: an optional
dependency gets a fallback and a message naming *which* precondition failed, never a generic one
that misattributes the cause. **Record the bug that motivated the routine** — the gotchas section
is the part that cannot be re-derived from the code. No secrets, no client PII; the client
engagement goes in `source:` frontmatter, never in the body.

## 3d. A prompt (your prompt library)

One `.md` per prompt inside a category dir (`audit-prompts/`, `ops-prompts/`, `reporting-prompts/`
— create a new category rather than stretching an existing one, and only when more than one
prompt will live in it). Frontmatter: `name`, `description` (fire/don't-fire conditions),
`output`, `evidence` (canonical vs degraded), `status`, `source`, `created`.

**Self-containment is the whole point.** A skill assumes the skill loader; a routine assumes the
scripts are on disk; a prompt assumes nothing but the model. Every named tool must carry an
inline fallback, because the prompt has to run in a cron `claude -p` lane with none of your
config. If it is only useful once a specific skill is loaded, it is that skill's body — move it.

House shape: intake gate (what to refuse to start without) → feasibility gate → degraded-mode
table → method → failure modes → a two-part **"what to hand back"** return contract, where the
second part asks what the prompt itself failed to say. New prompts land `status: draft`; a first
run teaches more than a review. `status` is the scoreboard: `draft` → `reviewed` → `live`, and a
prompt still at `draft` after two runs is the wrong prompt.

Keep `MANIFEST.yml` and the README index in step in the same commit.

## 3e. A repo's own `CLAUDE.md`

For a convention that binds exactly one codebase. Check whether a section already owns the topic
before adding one — these files are always-loaded for that repo, so length is a real cost. Match
the file's existing voice and table style. Prefer amending an existing row to appending a new
section. If the rule deserves teeth, pair it with a check (script/hook/gate) and let the
`CLAUDE.md` text carry only the *why* — prose-only rules are drafts.

## 4. A skill (your skill library)

New dir + `SKILL.md` (frontmatter `name:` + a pushy, MECE `description:`; body = trigger
conditions, numbered steps, pitfalls, verification). Symlink it into `~/.claude/skills/<name>`
so the harness registers it (`ln -s <skill-library>/<name> ~/.claude/skills/<name>`), or use
your library's own sync script to fan it out to every harness. If the
procedure is non-obvious or every agent would want it, prefer staging a card that proposes
the skill so the user signs off before it goes live. For a substantial new skill, the
`skill-creator` skill is the right tool.

**Receipt bar.** Every stated tool/system behavior must be marked `**Verified <yyyy-mm-dd>:**` (you
ran it) or `**Unverified:**` (inferred). Unlabelled confident claims are the defect — see
`hygiene-heuristics.md` check 7. Retract wrong claims **in place**, showing what was actually
tested; don't delete them silently.

**Then invoke it.** Writing a skill does not load it. Load the skill you just wrote and use it for
the rest of the session.

## 5. A card on your backlog (cross-harness, gated)

One backlog for anything needing the user's decision, or work that should be scheduled — whatever board or issue tracker you use. Canonical knowledge stores are never written directly; the gate is
a card. The things that bite:

- **Mint sequence numbers atomically.** Hand-computing `max(seq)+1` races any other writer.
- **Always set the field the board groups by.** A card missing it can exist in the table and
  never render — it is invisible to the user.
- A learning that needs the user's judgement gets a "not agent-runnable" flag with the gate named
  in its `why`. Before minting, query open cards and match on the subject so a cron does not
  re-file the same finding.
