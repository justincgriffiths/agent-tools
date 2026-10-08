# Routing rules — per-store format

Section numbers are the row numbers of the routing table in `SKILL.md`. Pick the row there,
then read **only** its section — reading this whole file to route one element is the waste the
table exists to stop:

    sed -n '/^## 6\./,/^## 7\./p' references/routing-rules.md     # row 6
    sed -n '/^## 11\./,$p'        references/routing-rules.md     # row 11, the last

## 1. Nothing

It is already in the session transcript. Don't manufacture an artifact to feel thorough.

## 2. A hook (`~/.claude/hooks/` + `settings.json`)

For a **mechanical guard** — "tool Y silently drops Z", "never call W without doing V first",
anything shaped "whenever X happens, do Y". Documentation only fires if the reader happens to
load it; a hook fires at the call site every time, regardless of which skill is in context.
Route the *enforcement* here and keep the human-readable *why* in whatever skill covers the
domain, each pointing at the other. The trap is reaching for a doc store because a doc is
what's already open.

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

A hook claim needs the "trigger the real tool once" proof above: a guard that is cited by a
skill but has vanished from disk (or was never wired) protects nothing while every reader
believes it does.

A skill that cites a hook is linted: `${CLAUDE_PLUGIN_ROOT}/skills/learn/scripts/hookrefs.sh` reports every
`~/.claude/hooks/<name>` a `SKILL.md` or `references/*.md` names that is MISSING, NOT-EXEC, or
UNWIRED in `settings.json`, so the next dead citation surfaces in a night, not two months.

## 3. A template (your template library)

The test is that the *output shape* is the reusable thing — a deck, a page, a contract, a report.
One kebab-case dir under a plural category (e.g. `webpages|pitches|contracts|analyses|reports|dashboards`),
carrying a `TEMPLATE.md` whose frontmatter is mandatory and complete: `name` (matches the dir),
`category`, `formats`, `source`, `created`, `brand`, `placeholders`, `status`. Body = when to
use it and how to fill it.

**Update `MANIFEST.yml` and the README index in the SAME commit** as any add/remove/rename —
this is the repo's own hard rule and drift here is a known recurring defect.

- **Edit here, never in a consumer mirror.** A synced mirror in a consumer repo is overwritten
  by the next sync; edits made there are destroyed silently. Before any sync, scan for drift you
  would clobber: `${CLAUDE_PLUGIN_ROOT}/skills/dedupe/scripts/scan-tree.sh --canonical
  <templates-repo> --vendored <consumer-mirror> --name templates`.
- **Placeholder syntax is per-family, do not migrate working systems.** `{{PLACEHOLDER}}` for
  HTML/web/email; `[Token.Name]` + `[[signature]]`/`[[date]]` for contracts.
- **Strip client PII** to generic example data (`dana@acme.com`, `Starlight LLC`). Named clients
  only as deliberate case-study content, never as leftover fill-in values.

## 4. A routine (your routine library)

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

## 5. A prompt (your prompt library)

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

## 6. A skill (your skill library)

New dir + `SKILL.md`: frontmatter `name:` + a pushy, MECE `description:` written as *when to
fire / when not to*; body = trigger conditions, numbered steps, pitfalls, verification. The
repo's own `CLAUDE.md` owns the rest — required frontmatter (`created:`, `source:`, `summary:`,
`group:`; unknown fields are blocked at commit), the ~300-line bar, the draft rule, and the
generated README index. Read it before authoring. For a substantial new skill, the
`skill-creator` skill is the right tool.

Don't hand-create a skill silently on a hunch. If it's non-obvious or cross-harness, open an
issue proposing it (row 10) so the user signs off before it goes live.

To register it, symlink it into `~/.claude/skills/<name>` or run your library's sync script
**from a clean checkout of `origin/main`** (a pinned worktree), never from a shared working
checkout — it is worth making the sync script refuse unless the checkout is clean and exactly
`origin/main`. Do not hand-symlink into a shared checkout; it is routinely on a feature branch.

**Receipt bar.** Do not write procedural guidance — and especially not a stated tool behavior —
that you have not exercised in this session. Inferred gotchas are worse than no gotchas: they
send every future agent down a wrong diagnostic path with full confidence. Mark each claim:
- `**Verified <yyyy-mm-dd>:**` — you ran it and observed the result.
- `**Unverified:**` — plausible but untested. Allowed, but must be labelled.

Unlabelled confident claims are the defect — see `hygiene-heuristics.md` check 7. If a claim
turns out wrong later, **retract it in place**, leaving the retraction visible with what was
actually tested. A silently-removed wrong claim teaches nothing and gets re-derived.

**Then invoke it.** Writing a skill does not load it. Load the skill you just wrote and use it for
the rest of the session.

## 7. A team knowledge base (glossary + how-to entries)

For a **term** or a **proven procedure** about your own machinery — what an internal flag
means, how to publish KB notes, the shape of a data contract. This is the store that compounds:
entries cross-link, so each addition makes the others more findable, and the knowledge base
renders them for anyone.

Two bars: a term must have been **looked up or explained twice**, and a how-to needs a
**receipt** — a session that actually ran it. Everything here is internal documentation, never
client-visible.

**The compounding rule.** A session that established a durable fact about our own
machinery should end by minting or updating at least one entry here. Not as a quota — if the
session genuinely established nothing new, forcing an entry produces exactly the confidently-wrong
content the receipt bar exists to prevent.

## 8. A repo's own `CLAUDE.md`

For a convention that binds exactly one codebase — its layout, its commit style, what must never
be edited in place, which skill supersedes a generic one there. It loads for everyone working in
that repo and nowhere else, which is usually the scope you actually want: cheaper and
better-targeted than a global directive.

Check whether a section already owns the topic before adding one — these files are
always-loaded for that repo, so length is a real cost. Match the file's existing voice and table
style. Prefer amending an existing row to appending a new section. If the rule deserves teeth,
pair it with a check (script/hook/gate) and let the `CLAUDE.md` text carry only the *why* —
prose-only rules are drafts.

## 9. `~/.claude/CLAUDE.md` (global, every project)

Only for a standing directive that must apply everywhere. **Confirm with the user before
editing** — it's always-on, affects every Claude Code session, and costs context on every turn.
Keep additions short and in the existing voice. If the behavior is automated ("whenever X
happens…"), it is row 2, a hook via the `update-config` skill, not this.

## 10. A GitHub issue in the owning repo (cross-harness, gated)

For anything needing the user's decision or a schedule, a fix nobody can do tonight, or canonical
knowledge that should outlive this harness — an architecture decision, a domain truth every
agent should share.

**Prefer per-repo issues over a separate card board.** The backlog lives where the work does: an
issue — or a PR when the artifact is code — in the repo that owns it (the app repo, the
ops/scripts repo, the skill/routine libraries for harness tooling). A canonical knowledge store
is still never written directly; the gate is an issue labelled with a gate label (e.g.
`gate:owner`).

A shape that works:

- **Title** names the job, not the domain. **Body** in three parts: where it stands (facts,
  timestamps, shas, run ids), what's needed with the actor per step, **done means**.
- **Labels** from the repo: `lane:*`, the gate label when only the user can decide, `P0`–`P3`,
  `bug`, `parent` for an epic. `gh label list --repo <r>` before guessing.
- **One issue per finding.** `gh issue create --repo <r> --title … --label … --body-file -`
  with a heredoc. Before opening, `gh issue list --repo <r> --state open --search "<subject>"`
  so a scheduled run does not re-file the same finding.
- **Two per command, not eight.** If a guard hook refuses commands containing certain phrases
  (e.g. "force-push"), one such body kills a whole batch of creates. Say "rewrite shared
  history".
- **Cross-reference.** An issue that has a PR says so; a PR that partially fixes an issue says
  which half. An item migrated from another tracker names its old id on the first line.

> **If you still use a card board,** the same rules hold: one card per finding, the gate named,
> and a field that marks it not-agent-runnable. Avoid a markdown review queue — a file nobody is
> notified about is a decision nobody makes.

## 11. CC project memory (`~/.claude/projects/<encoded-cwd>/memory/`) — LAST RESORT

**The bar: memory holds live project STATE, not knowledge.** *"Card 295 is blocked on Touch
ID"*, *"the proposal went out 8/12 with Terms removed"* — state. *"How to build a 90-day
plan"*, *"the HTML→PDF recipe"*, *"never narrate git"* — knowledge, and every one of those
belongs in a library. **The test:** *would this still be true and useful in six months?* If
yes, it is not memory — go back up the table.

Memory is also often the only store with **no remote** — `~/.claude` is frequently not under
version control at all. Anything written here may be laptop-only. Never route something you would hate to lose.

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
