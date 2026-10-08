---
name: learn
description: "Decompose what a session did into REUSABLE ELEMENTS and route each to the store that owns it — a skill, a routine, a template, a prompt, a hook, a repo CLAUDE.md, a backlog card, a team knowledge base, or (last resort) this project's Claude Code memory. ALSO audits the skill library for overlap and bloat. Use this WHENEVER the user says 'capture learnings', 'save what I learned', 'remember this for next time', 'break this down into reusable parts', at session end or before /archive, OR asks to 'audit my skills', 'are my skills overlapping', 'clean up my skill library', 'is my skill library MECE'. Can also run on a schedule as a skill-hygiene sweep. Routes mechanical guards to hooks by handing off to update-config; it does not wire them itself."
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
summary: "Route a durable learning to the right store (nothing / project memory / CLAUDE.md / **hook** / new skill / team KB / backlog card) AND audit the skill library for overlap + correctness. Enforcement-first: mechanical guards against misbehaving tools go to hooks via `update-config`, not prose. Receipt bar (`Verified`/`Unverified`) on skill guidance; hygiene checks 7–8 catch confidently-wrong claims and skills that never fire."
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
(hook), the convention (a repo's CLAUDE.md), the decision someone owes (card). One session
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
> **last** branch, and it has a bar (see branch 11).

### The load-bearing fact

Claude Code **memory is per-project** — it lives at
`~/.claude/projects/<encoded-cwd>/memory/` and is only loaded when Claude Code runs in that
working directory. A memory saved while `cwd=~/project-a` is invisible to a session in `~/project-b`.
`~/.claude/CLAUDE.md` is per-machine (every Claude Code project). A shared knowledge store (a
notes repo, a team KB) is cross-**harness** (Claude Code *and* every other agent you run).
So the first routing question is always:
**what is the smallest scope that still sees this when it's needed — this project, all of my
Claude Code, or every agent I run?**

### The stores

| Store | Scope | Right for |
|-------|-------|-----------|
| Session history | this project, searchable | "I just want to find this conversation later" → do nothing |
| A hook (`~/.claude/hooks/` + `settings.json`) | fires at the call site, no loading required | a mechanical guard against a misbehaving tool — the only store that **enforces** rather than informs |
| **Template library** | synced into consumer repos | **the output shape is the artifact** — a deck, page, contract, report scaffold |
| **Routine library** | invokable, runnable | **the steps are fixed and a script can run them.** Must ship `.sh`/`.py` + a verify gate |
| **Prompt library** | any harness, no config | **a stranger session must do the whole job from one pasted block** — cold CC, `claude -p`, a teammate, another vendor |
| A skill (skill library) | invokable across CC | **judgment** — what to watch for, what a check cannot catch, which path to take |
| Team KB (glossary + how-to entries) | any agent or human via your knowledge base | a **term** or a **proven procedure** about your own machinery |
| **A repo's own `CLAUDE.md`** | everyone working in that repo | a convention that binds **one** codebase — layout, commit style, what never to edit |
| `~/.claude/CLAUDE.md` | all CC projects, every turn | a standing directive that must apply everywhere (heavier — confirm first) |
| Card on your backlog board | cross-harness, all agents, one backlog | anything needing the user's decision, or work that should be scheduled |
| CC project memory (`~/.claude/projects/<cwd>/memory/`) | per-project, recalled by relevance | **last resort.** Live project *state* only — see branch 11 |

**The four libraries are siblings, and their boundary is worth writing down once** — in one
library's `CLAUDE.md` that the others point to:

> **skill** = judgment · **routine** = exact steps a script can run · **template** = the output
> shape is the artifact · **prompt** = a stranger session does the whole job from one block

If a prompt is only useful when a specific skill is already loaded, it is a skill's body, not a
prompt. If an agent has to re-derive the commands from a description, it is a skill, not a
routine.

### Routing decision tree

Run this **per element**, not per session. Ask in order — stop at the first yes. The order is
deliberate: stores that *act* come before stores that *inform*, and memory is last.

1. **Just "find this later"?** → do nothing. It's in the session transcript. Don't manufacture
   an artifact.
2. **A mechanical guard against a misbehaving tool** — "tool Y silently drops Z", "never call W
   without first doing V"? → a **hook**, via the `update-config` skill. Not a doc.

   Documentation only fires if the reader happens to load it. A hook fires at the call site, every
   time, regardless of which skill is in context. Route the *enforcement* to a hook and keep the
   human-readable *why* in whatever skill covers the domain. Cross-reference the two.

   The trap: reaching for a doc store because a doc is what's already open. If the learning is
   "whenever X happens, do Y," that is a hook by definition.

3. **Did the session produce an ARTIFACT whose shape will be wanted again** — a deck, a page, a
   contract, a report, a one-pager? → a **template** in your template library. The test is that
   the *output shape* is the reusable thing. Edit there, never in a consumer mirror
   (a synced mirror is overwritten by the next sync). Every template dir needs
   a `TEMPLATE.md` with full frontmatter, plus `MANIFEST.yml` and README index updates **in the
   same commit**. Strip client PII to generic example data.

4. **Did the session settle a fixed sequence of commands** that ran, or should run, the same way
   next time? → a **routine** in your routine library. The bar is real: it ships `.sh`/`.py`
   taking arguments, and it **ends in a verify gate** — no artifact without a check that the
   artifact is correct. No gate means `status: draft`. Record the bug that motivated it; the
   gotchas section is the part that cannot be re-derived from the code.

   If an agent would have to re-derive the commands from your description, you have a skill, not
   a routine. Don't file prose here.

5. **Will this work need to run in a session that does not have your config** — a cold CC
   session, `claude -p`, Claude Design, a teammate's machine, another vendor's model? → a
   **prompt** in your prompt library. It must be self-contained: a skill assumes the skill
   loader, a routine assumes the scripts are on disk, a prompt assumes nothing but the model.
   Follow the house shape (intake gate, feasibility gate, degraded-mode table, method, failure
   modes, a "what to hand back" return contract). New prompts land `status: draft` — a first run
   teaches more than a review.

6. **A reusable JUDGMENT** — what to watch for, what a check cannot catch, which of several
   paths to take? → a skill in your skill library. Don't hand-create it silently on a hunch; if
   it's non-obvious or cross-harness, stage it as a card so the user signs off.

   **Receipt bar — this branch has one too.** Do not write procedural guidance, and especially not
   a stated tool behavior, that you have not exercised in this session. Inferred gotchas are worse
   than no gotchas: they send every future agent down a wrong diagnostic path with full confidence.
   Mark each claim:
   - `**Verified <yyyy-mm-dd>:**` — you ran it and observed the result.
   - `**Unverified:**` — plausible but untested. Allowed, but must be labelled.

   If a claim turns out wrong later, **retract it in place** — leave the retraction visible with
   what was actually tested, rather than quietly deleting it. A silently-removed wrong claim
   teaches nothing and can be re-derived by the next agent.
7. **A term or a proven procedure about YOUR OWN machinery** — what an internal flag means,
   how to publish KB notes, the shape of a data contract? → your team KB, as a glossary or
   how-to entry. This store is the one that
   compounds: entries cross-link, so each addition makes the others more findable, and the
   knowledge base renders them for anyone. Two bars to clear — a term needs to have been **looked
   up or explained twice**, and a how-to needs a **receipt** (a session that actually ran it).
   Everything here is internal documentation, never client-visible.
8. **A convention that binds ONE repo** — its layout, its commit style, what must never be
   edited in place, which skill supersedes a generic one here? → that repo's own `CLAUDE.md`.
   It loads for everyone working in that codebase and nowhere else, which is usually the
   scope you actually want. Cheaper and better-targeted than a global directive; check whether
   the repo already has a section that owns the topic before adding one.

9. **A standing behavioral rule for EVERY project** ("always phrase commits like…")? → propose
   an edit to `~/.claude/CLAUDE.md`, but **confirm with the user first** — it's always-on and
   global, and it costs context on every single turn. If it's an *automated* "whenever X, do Y"
   behavior, that's branch 2, a hook.

10. **Canonical knowledge that should outlive this harness** — an architecture decision, a domain
   truth every agent should share? → a **card** on your backlog board (see
   `references/routing-rules.md` §5). Set the grouping field or the card exists but never
   renders. User-gated cards are flagged not-agent-runnable with the gate named in `why`.
   Canonical knowledge stores are never written directly — the gate is a card.

11. **Everything else — and only what genuinely fits nowhere above** → CC project memory. One
   fact per file, format per `~/.claude/CLAUDE.md`, one-line `MEMORY.md` pointer, declarative
   ("X is Y") not imperative.

   **The bar: memory holds live project STATE, not knowledge.** *"Card 295 is blocked on Touch
   ID"*, *"the proposal went out 8/12 with Terms removed"* — state. *"How to build a 90-day
   plan"*, *"the HTML→PDF recipe"*, *"never narrate git"* — knowledge, and every one of those
   belongs in a library.

   **The test:** *would this still be true and useful in six months?* If yes, it is not memory —
   go back up the tree. If it will be stale by then, memory is correct.

   Memory is also often the only store with **no remote** — `~/.claude` is frequently not under
   version control at all. Anything written here may be laptop-only. Never route something you
   would hate to lose.

A single session normally yields **several** elements — a template AND a routine AND a card. If
you finish this tree having produced one artifact, re-read what the session actually built; you
have probably described it instead of decomposing it.

**Enforcement beats documentation.** Branches 7–11 all produce text that only helps if someone
reads it at the right moment. Branches 2–5 produce things that fire, run, or get pasted. When an
element could plausibly route either way, prefer the lower number and let the doc carry the
explanation — a gated card describing a tool bug is the least likely artifact to ever change
behavior.

**The compounding rule.** A session that established a durable fact about our own
machinery should end by minting or updating at least one glossary or how-to entry. Not as a
quota — if the session genuinely established nothing new, forcing an entry produces exactly the
confidently-wrong content the receipt rule exists to prevent. But the default expectation for a
research or deep-dive session is that *something* was looked up twice and now deserves an entry.

Full per-store format rules and the exact card mechanics live in
`references/routing-rules.md` — read it before writing to any store.

### Procedure

1. **Decompose first.** List what the session *built or settled*, one line each — not what you
   "learned". Artifacts produced, command sequences that worked, judgment calls made, guards
   discovered, conventions established, decisions owed to someone. Ask "what has a second use?"
   Expect three to five items on a substantial session; one item usually means you summarized
   instead of decomposing.
2. **Ask whether a skill already covered this work — and whether it was actually invoked.** Check
   the available-skills listing against what the session did. If a skill existed and went
   uninvoked, that is a **trigger defect**, not a shrug: the description failed to fire. Record it
   as a Mode B finding (see `references/hygiene-heuristics.md`, check 7) and propose the retune.
3. Classify each learning via the tree. Most sessions yield zero or one durable artifact — fine.
4. Write the artifacts (see `references/routing-rules.md` for each store's format and, for
   cards, the atomic-numbering rule).
5. **Invoke the skill you just wrote or edited, and use it for the rest of the session.** Writing
   a skill does not load it. Authoring it from working memory leaves the guidance out of context
   precisely when it applies, and the session that just created a skill is usually the one about to
   need it. Verified failure, 2026-07-28: a Notion skill was written mid-session, registered in the
   skill list, and then never loaded — the session went on to hit two of the exact failures the new
   skill described. Load it, then continue.
6. **Verify each artifact would have caught the failure it came from.** Read it back as if you were
   the next agent: does it change what you'd do? An artifact that merely *describes* the incident
   is a diary entry. If nothing about it would alter behavior, route it to branch 4 (a hook) or
   drop it.
7. Report one line per artifact: what went where and why. For anything gated (card, CLAUDE.md
   edit), say it's **waiting for approval** — don't claim it's live. Say explicitly which claims are
   `Verified` and which are `Unverified`.

---

## Mode B — skill-library hygiene audit

The "make suggestions regularly" half. Sweep your skill library for the problems that make a skill
library slow and imprecise, and stage each finding as a **card** — a *suggestion*, never an
applied edit. This is what a scheduled run invokes.

**Never edit or delete a skill in this mode.** The card proposes the change; the user approves;
a later session applies it. Silent edits to a working skill are the failure mode.

### Procedure

1. Run `scripts/scan-skills.sh [<skill-library-dir>]` to get the current inventory (name, line count, first-40-word
   description, resource dirs) without re-deriving it by hand.
2. Apply the checks in `references/hygiene-heuristics.md`:
   - **Overlap / MECE** — two+ descriptions competing for the same trigger phrases.
   - **Bloat** — SKILL.md over ~300 lines (push detail to `references/`).
   - **Broken frontmatter** — missing `name:`/`description:`, or no YAML block at all.
   - **Near-duplicate purpose** — two skills that do substantially the same job.
3. For each *distinct* finding, mint one card flagged not-agent-runnable, with its grouping
   field set, the problem in `why` and the concrete fix in its actions. One card per finding —
   don't bundle.
4. Skip findings already staged in a prior run: query open (backlog/todo) cards and
   match on the skill name before minting, so a scheduled run doesn't re-file the same suggestion.
5. Report a summary: N findings, M new cards staged, K skipped-as-already-open. If the library is
   clean, say so and stage nothing — a quiet run is a good run.

---

## Pitfalls

1. **Writing a canonical knowledge store directly** — always a user-gated card instead. Applies to
   Mode A canonical learnings and every Mode B suggestion.
2. **Over-capturing** — not every session has a durable learning; not every skill needs a card.
   Manufacturing artifacts for one-offs is slop. A quiet run is fine. But note the *opposite*
   failure is the one with 114 files behind it (pitfall 6) — under-decomposing is the common
   error, over-capturing the rarer one.
3. **Wrong scope** — a fact every project needs, saved only to this project's memory, is invisible
   elsewhere. Re-ask the scope question (per-project / all-CC / cross-harness).
4. **Editing a skill in Mode B** — Mode B only *suggests*. The one exception is if the user approves
   a card live and says "apply it," in which case make the edit in that session.
5. **Colliding with `update-config`** — automated "whenever X, do Y" behaviors are hooks, not
   memories. Route those to `update-config`, don't write them as a memory that reads as a wish.
6. **Memory as the default sink.** The named failure. Memory used to be branch 2 and its test
   caught everything, so one project's `~/.claude/projects/<project>/memory/` reached **114 files**
   holding recipes, design rules and procedures that were all really skills, routines or
   templates. Symptoms you are repeating it: writing a memory whose title starts with a verb;
   writing one that would still be true in six months; writing one because you did not want to
   meet a library's bar (a routine needs a verify gate, a template needs `TEMPLATE.md` +
   MANIFEST). Meet the bar or route it to a card — do not downgrade it into memory.
7. **Describing instead of decomposing.** Producing one artifact called
   "what-happened-in-session-X" from a session that built four reusable things. The tell is a
   filename that names an *event* rather than a *thing*.
