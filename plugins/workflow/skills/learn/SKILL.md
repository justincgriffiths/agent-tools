---
name: learn
description: "Decompose what a session did into REUSABLE ELEMENTS and route each to the store that owns it — hook, template, routine, prompt, skill, team KB, repo CLAUDE.md, a GitHub issue in the owning repo, or (last resort) project memory. ALSO audits the skill library for overlap and bloat; can run on a schedule as a skill-hygiene sweep. Use WHENEVER the user says 'capture learnings', 'save what I learned', 'remember this for next time', 'break this down into reusable parts', at session end or before /archive, the moment a tool or skill proves wrong mid-session, OR 'audit my skills', 'are my skills overlapping', 'clean up my skill library', 'is my skill library MECE'. SKIP wiring a hook itself — hand that to update-config."
argument-hint: "[audit] — bare = capture this session's learnings; 'audit' = sweep the skill library"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
created: 2026-07-07
source: extracted from the author's working sessions, 2026
summary: "Route each reusable element of a session to the store that owns it, in order (**hook** / template / routine / prompt / skill / team KB / repo CLAUDE.md / GitHub issue / project memory last) AND audit the skill library for overlap + correctness. Enforcement-first: mechanical guards against misbehaving tools go to hooks via `update-config`, not prose. Receipt bar (`Verified`/`Unverified`) on skill guidance; hygiene checks 7–8 catch confidently-wrong claims and skills that never fire."
group: "Capture & meta"
---

# Learn

"Save my learnings" is a **routing** problem, not one destination. It has two modes.

- **Bare invocation / "capture learnings" / session end** → Mode A (route session learnings).
- **`audit` / "clean up my skills" / a scheduled run** → Mode B (skill-library hygiene).

Pick by the argument and the user's phrasing. If genuinely unclear, ask one line.

**Mode A also fires mid-session, not just at the end.** A tool that returned success while doing
nothing, or a skill whose own guidance turned out to be wrong, is a capture trigger *right then* —
the session holding the evidence is the only one that can verify the guard. Deferring it to session
end means the fix gets written from memory of the failure instead of from the failure itself.

---

## Mode A — decompose the session into reusable elements, then route each

**The job is decomposition, not filing.** Take what the session actually did and break it into
the reusable parts hiding inside it: the judgment call worth reusing (skill), the exact command
sequence (routine), the artifact shape (template), the pasteable brief (prompt), the guard
(hook), the convention (a repo's CLAUDE.md), the decision someone owes (issue). One session
routinely yields three or four of these. Asking "what did I learn?" produces one vague note;
asking "what did I *build* that has a second use?" produces the elements.

The failure mode is dumping everything into one store — historically **memory**, which is
write-only: it loads as context and hopes the next agent reads it. Everything else on the list
gets *invoked*. Prefer a store that does something over a store that says something.

> **Evidence this is real (2026-08-13).** One project's `~/.claude/projects/<project>/memory/` held
> **114 files** — every feedback rule, recipe and archive for that project — because memory used to be
> branch 2 of a stop-at-first-match tree and its test ("a fact/preference/state for THIS
> project") catches nearly everything. The four libraries were not branches at all. The user's
> ruling: all of it belonged in skills, routines, templates and prompts. Memory is now the
> **last** row, and it has a bar (row 11).

### The load-bearing fact

Claude Code **memory is per-project** — it lives at
`~/.claude/projects/<encoded-cwd>/memory/` and is only loaded when Claude Code runs in that
working directory. A memory saved while `cwd=~/project-a` is invisible to a session in `~/project-b`.
`~/.claude/CLAUDE.md` is per-machine (every Claude Code project). A shared knowledge store (a
notes repo, a team KB) is cross-**harness** (Claude Code *and* every other agent you run).
So the first routing question is always:
**what is the smallest scope that still sees this when it's needed — this project, all of my
Claude Code, or every agent I run?**

### The routing table

Run it **per element**, not per session. Ask in order and stop at the first yes. Stores that
*act* come before stores that *inform*, and memory is last.

| # | Stop here if… | Store |
|---|---|---|
| 1 | You only want to find this conversation again | **nothing** — it's in the transcript |
| 2 | It's a mechanical guard: "tool Y silently drops Z", "never W without V". Any "whenever X, do Y" is a hook by definition | a **hook**, via `update-config`. The *why* goes in the domain skill |
| 3 | The session produced an artifact whose **output shape** will be wanted again — deck, page, contract, report | a **template** in your template library |
| 4 | It's a fixed command sequence a script can run, ending in a verify gate. If an agent would have to re-derive the commands from prose, it's a skill | a **routine** in your routine library |
| 5 | It must run where your config isn't — a cold session, `claude -p`, Claude Design, a teammate, another vendor | a **prompt** in your prompt library |
| 6 | It's reusable judgment — what to watch for, what a check can't catch, which path to take | a **skill** in your skill library. The receipt bar applies |
| 7 | It's a term or a proven procedure about your own machinery, looked up twice or actually run | your **team KB** (glossary / how-to entries) |
| 8 | It's a convention binding exactly one repo | that repo's **`CLAUDE.md`** |
| 9 | It's a standing rule for every project | **`~/.claude/CLAUDE.md`** — confirm with the user first |
| 10 | It needs the user's decision or a schedule, or should outlive this harness | a **GitHub issue** in the owning repo (or your tracker's equivalent), with a gate label |
| 11 | Nothing above fits, **and** it will be stale in six months | **CC project memory** — live state only |

Row 11 is a test, not a sink. If the thing would still be true and useful in six months, it is
knowledge, and knowledge belongs higher up the table.

**Before writing, read only the matching section of `references/routing-rules.md`.** Its
section numbers are these row numbers, and each section carries that store's format, bar and
gotchas. Reading the whole file to route one element is the waste this table exists to stop.

The four libraries are siblings, and their boundary is worth writing down once — in one
library's `CLAUDE.md` that the others point to:

> **skill** = judgment · **routine** = exact steps a script can run · **template** = the output
> shape is the artifact · **prompt** = a stranger session does the whole job from one block

A single session normally yields **several** elements — a template AND a routine AND an issue.
If you finish the table having produced one artifact, re-read what the session actually built;
you have probably described it instead of decomposing it. A research or deep-dive session
should normally end with at least one row-7 entry, because something was looked up twice
(the compounding rule, in section 7).

**Enforcement beats documentation.** Rows 2–5 produce things that fire, run, or get pasted.
Rows 6–11 produce text that only helps if someone reads it at the right moment — a skill
included, since writing one does not make it load. When an element could plausibly route either
way, take the lower number and let the doc carry the explanation — a gated issue describing a
tool bug is the least likely artifact to ever change behavior.

### Procedure

1. **Decompose first.** List what the session *built or settled*, one line each — not what you
   "learned". Artifacts produced, command sequences that worked, judgment calls made, guards
   discovered, conventions established, decisions owed to someone. Ask "what has a second use?"
   Expect three to five items on a substantial session; one item usually means you summarized
   instead of decomposing.
2. **Ask whether a skill already covered this work — and whether it was actually invoked.** Check
   the available-skills listing against what the session did. If a skill existed and went
   uninvoked, that is a **trigger defect**, not a shrug: the description failed to fire. Record it
   as a Mode B finding (see `references/hygiene-heuristics.md`, check 8) and propose the retune.
3. Classify each element via the table. Most sessions yield zero or one durable artifact — fine.
4. Write the artifacts, reading only the `references/routing-rules.md` section numbered for
   each row you picked.
5. **Invoke the skill you just wrote or edited, and use it for the rest of the session.** Writing
   a skill does not load it. Authoring it from working memory leaves the guidance out of context
   precisely when it applies, and the session that just created a skill is usually the one about to
   need it. Verified failure, 2026-07-28: a Notion skill was written mid-session, registered in the
   skill list, and then never loaded — the session went on to hit two of the exact failures the new
   skill described. Load it, then continue.
6. **Verify each artifact would have caught the failure it came from.** Read it back as if you were
   the next agent: does it change what you'd do? An artifact that merely *describes* the incident
   is a diary entry. If nothing about it would alter behavior, route it to row 2 (a hook) or
   drop it.
7. Report one line per artifact: what went where and why. For anything gated (an issue, a
   CLAUDE.md edit), say it's **waiting for approval** — don't claim it's live. Say explicitly
   which claims are `Verified` and which are `Unverified`.

---

## Mode B — skill-library hygiene audit

The "make suggestions regularly" half. Sweep your skill library for the problems that make a skill
library slow and imprecise, and stage each finding as a **GitHub issue** in the skill library's
repo — a *suggestion*, never an applied edit. This is what a scheduled run invokes.

**Never edit or delete a skill in this mode.** The issue proposes the change; the user approves;
a later session applies it. Silent edits to a working skill are the failure mode.

### Procedure

1. Run `scripts/scan-skills.sh [<skill-library-dir>]` to get the current inventory (name, line count, first-40-word
   description, resource dirs) without re-deriving it by hand.
2. Apply the checks in `references/hygiene-heuristics.md`:
   - **Overlap / MECE** — two+ descriptions competing for the same trigger phrases.
   - **Bloat** — SKILL.md over ~300 lines (push detail to `references/`).
   - **Broken frontmatter** — missing `name:`/`description:`, or no YAML block at all.
   - **Near-duplicate purpose** — two skills that do substantially the same job.
   - **Stale provenance** — missing or outdated `created:`/`source:`.
   - **Oversized description** — the frontmatter blurb loads in every session, not just on fire.
   - **Unverified assertion** — stated tool behaviour nobody exercised (correctness, not form).
   - **Trigger miss** — a skill existed, applied, and did not fire.
3. For each *distinct* finding, open one issue labelled with your gate label (e.g. `gate:owner`), the
   problem in the body and the concrete fix as a checklist. One issue per finding — don't
   bundle.
4. Skip findings already staged in a prior run: run
   `gh issue list --repo <owner>/<skill-library> --label <gate-label> --state open` and
   match on the skill name before minting, so a scheduled run doesn't re-file the same suggestion.
5. Report a summary: N findings, M new issues opened, K skipped-as-already-open. If the library
   is clean, say so and stage nothing — a quiet run is a good run.

---

## Pitfalls

1. **Writing a canonical knowledge store directly** — always a user-gated issue instead. Applies to
   Mode A canonical learnings and every Mode B suggestion.
1b. **Minting a markdown card in a review queue** instead of an issue. A file nobody is notified
   about is a decision nobody makes; if you are about to write `NN-slug.md`, open an issue instead.
2. **Over-capturing** — not every session has a durable learning; not every skill needs an issue.
   Manufacturing artifacts for one-offs is slop. A quiet run is fine. But note the *opposite*
   failure is the one with 114 files behind it (pitfall 6) — under-decomposing is the common
   error, over-capturing the rarer one.
3. **Wrong scope** — a fact every project needs, saved only to this project's memory, is invisible
   elsewhere. Re-ask the scope question (per-project / all-CC / cross-harness).
4. **Editing a skill in Mode B** — Mode B only *suggests*. The one exception is if the user approves
   an issue live and says "apply it," in which case make the edit in that session.
5. **Colliding with `update-config`** — automated "whenever X, do Y" behaviors are hooks, not
   memories. Route those to `update-config`, don't write them as a memory that reads as a wish.
6. **Memory as the default sink.** The named failure behind the 114 files above. Symptoms you are
   repeating it: writing a memory whose title starts with a verb; writing one that would still be
   true in six months; writing one because you did not want to meet a library's bar (a routine
   needs a verify gate, a template needs `TEMPLATE.md` + MANIFEST). Meet the bar or route it to an
   issue — do not downgrade it into memory.
7. **Describing instead of decomposing.** Producing one artifact called
   "what-happened-in-session-X" from a session that built four reusable things. The tell is a
   filename that names an *event* rather than a *thing*.
