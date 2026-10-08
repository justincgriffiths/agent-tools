---
name: naming
description: Decide what to CALL a thing and where it goes before creating it — a new skill/routine/template/prompt, a directory, a script, a frontmatter field, a command invocation, a file/media record, a git branch or worktree, or a background session. Load BEFORE authoring or renaming a batch (including a sweep of the agents list), before `git checkout -b` / `git worktree add` / EnterWorktree, when a name feels arbitrary, when two things want the same name, or when you are about to invent a frontmatter field. A reusable house grammar for a personal or team library of agent skills; the judgment is here, enforcement belongs in your own linter.
intake:
  verbs: [place, name, invoke, field, audit]
  required: [thing]
  optional: [library, purpose]
created: 2026-08-17
source: extracted from the author's working sessions, 2026 — four libraries had four names for the date field, five invocation grammars across seven argument-hints, and six skills missing from an index a prose rule said to keep current
summary: "The house grammar: which library owns a thing, what it is called, how it is invoked. Cheat sheet in `references/`; enforce it with a linter + generator of your own"
group: "Capture & meta"
---

A house grammar for a library of agent skills (and their siblings: routines, templates,
prompts). Three questions in order — **which library owns it**, **what it is called**,
**how it is invoked** — then a checker takes over. Adopt it as-is or rename the libraries
to fit your own layout; the judgment transfers either way.

- One-page lookup: [`references/CHEATSHEET.md`](references/CHEATSHEET.md)
- The invocation contract in full: [`references/invocation.md`](references/invocation.md)
- What to do when a slot is missing: [`references/asking.md`](references/asking.md)
- One concept, one word — the semantic tier: [`references/vocabulary.md`](references/vocabulary.md)
- The body and the shape of a unit: [`references/unit-grammar.md`](references/unit-grammar.md)
- Scoring a unit against the grammar: [`references/rubric.md`](references/rubric.md)
- Enforcement: a linter + generator you own, in four tiers (generate · block · report · settle) — §5

> **A retraction worth keeping.** An earlier version of this page said the enforcement tool
> was missing from the main checkout of its library. **That was wrong.** It was on
> `origin/main` — `git ls-tree origin/main` listed every file. What was actually true was
> narrower: the main checkout was *checked out* on a feature branch that diverged before the
> merge, so the directory was absent from the working tree while present in the repo. The fix
> is `git checkout main`, not a path into a worktree — and paths written from the wrong
> conclusion resolve only until that worktree is re-cut (cron gotcha 9, turned on its author).

> **The rule this skill exists to obey:** enforcement beats documentation. Every
> rule below that a machine can adjudicate **should be** adjudicated — by a linter at
> commit time or by a generator that makes the mistake unrepresentable. Anything
> here with no check behind it is explicitly marked *judgment*, and that marking is
> the honest part: it says "you will have to think, and no cron will save you."

## 1. Which library owns it

Ask what would be *lost* if you put it elsewhere. The four libraries are not four
folders; they are four answers to different questions.

| Put it in | When | The test |
|---|---|---|
| `skills/` | The reader has your `~/.claude` and needs **judgment** | Remove the prose and the value is gone |
| `routines/` | The steps are **fixed** and a script can run them | An agent would re-derive the same commands every time |
| `templates/` | The **output shape** is the artifact | You are describing what the deliverable looks like |
| `prompts/` | A **stranger session** must do the whole job from one pasted block | It must work on a machine with none of your config |

Two failure modes, both real:

- **A routine wearing a skill's clothes.** If the whole body is a command sequence,
  it is a routine. Ship the script there and reference it. `deck-ship` (judgment:
  which destination) vs `deck-to-pdf` (commands) is the reference split.
- **A skill wearing a prompt's clothes.** If it only works once a specific skill is
  loaded, it is that skill's body, not a prompt.

*Judgment.* No check can make this call. A linter will happily validate a
perfectly-named thing in the wrong library.

## 2. What it is called

**Everything is kebab-case.** Directories, script filenames, frontmatter keys, intake
slots, verbs, flags. One shape, no exceptions to remember.

```
audit-landing-page  deck-to-pdf         monthly-performance-update
--dry-run           reviewed-by         first-run
```

Four modifiers:

| Shape | Means | Example |
|---|---|---|
| `_` prefix | **not a callable unit** — scaffold, staging dir, asset pack | `_shared/`, `_template-monthly.md`, `_epics/` |
| `-common` suffix | shared asset pack, **no entry doc** | `research-common/` |
| `SCREAMING.md` | the canonical doc of its directory | `SKILL.md`, `ROUTINE.md`, `MANIFEST.yml` |
| `snake_case` dir | a **Python package** — the import system requires it | `my_slides/` |

Categories are plural, units are singular things: `contracts/audit-full/`,
`audit-prompts/meta-audit.md`. Dates are ISO `yyyy-mm-dd`, everywhere, in every
field, forever.

### Units vs records — two grammars

Everything above governs a **unit**: a thing you invoke or open by name. A
**record** is a row in a set, one of thousands, named to be sorted and parsed by
a machine. Records use `_` between **fields** and `-` **inside** a field, because
a record is a tuple, not a phrase:

```
deck-to-pdf                                    unit
acme_2026-08-15_email_prospects_promo_fall-sale_a  record
2023-08-05_2056_iphone-13-mini_img-3151.mov      record (media)
```

Three record grammars are common — email-platform campaigns, ad names, media files — and
two of their rules look like violations of this page but are not (`xna` as a
value, a `<client>_` prefix). Media naming has four rules that were each paid
for, the sharpest being **never name from a UTC timestamp**.

Full treatment: [`references/records.md`](references/records.md). Per-platform
UTM parameter specs belong in their own conventions doc, not here.

*Checked:* kebab-case on units and scripts, entry-doc presence, `name:` matching the
directory. *Judgment:* whether the name says what the thing is. `app-page` and
`app-home` both pass the checker; whether they are one skill is your call.

### Branches and worktrees — the third grammar

A unit is invoked, a record is sorted, and a **branch or worktree is a place work
physically happens**. That earns one element the other two do not have: the device.

```
<type>/<slug>[-<device>]          feat/deletion-lane-devbox
<worktrees-root>/<slug>-<device>  .claude/worktrees/photo-stall-laptop2
```

`device` is a canonical name from a device registry you keep (e.g. a `devices.yaml`),
lowercased — e.g. `devbox` · `laptop2` · `homeserver`. Never a hostname, a former name, or a
kind (`mini`, `air`).

**Tag when the device is falsifiable, not when it is merely mentioned.** Would this
behave differently, or be unverifiable, on another machine? Tag it if it touches a
plist or a `hosts:`-declared job, writes per-host state, needs a credential or
volume that lives on one box — or if it is a **worktree**, which is a physical
directory and so is always tagged. Leave it off for skills, docs and library code,
where "it worked on my machine" is not a meaningful sentence. An omitted tag is a
claim too: *this runs anywhere*.

**The device is a tag, never the namespace.** `host/**` is rejected. A namespace is
a category, and putting a machine there invites a permanent per-machine line of
development — which is what left one repo's `main` 72 commits behind every branch.
The slug is a description; a device there says only *where the work runs*.

New as of 2026-09-18 and worth trying for one reason: a device tag is the **only
naming element a machine can verify** — `scutil --get LocalHostName` agrees with it
or it does not. Which also means a stale tag is worse than none, so a branch is
renamed when its work moves, and merged and deleted like any other.

Full treatment, the prior-art post-mortem and the checks:
[`references/branches.md`](references/branches.md).

### Background sessions — the fourth grammar

A background session is a row in a list the user scans to decide **what to keep**, so it
is the one grammar whose name carries lifecycle:

```
[STATUS_][NNN_]TAG_slug     YOU_014_BLD_copy-accuracy-audit    DEL_BAU_rsvp-and-block-time
```

- **`STATUS`**: whose move is next, `YOU` · `AGT` · `DEL`. The only slot re-set after
  naming, on every sweep.
- **`NNN`**: a claimed durable thread. One slug, one thread: a continuing session
  rejoins its claimed number and never mints a second one.
- **`TAG_slug`**: the kind of work and the job. `SCREAMING` tag and `_` separators
  break the kebab rule on purpose, because nothing imports a session by name. The
  client ban still holds.

Enforcement belongs to whatever names your sessions (a small session-naming script), not the
library linter, which never sees a session. Why the status exists, how to choose one, and the
duplicate-number post-mortem:
[`references/sessions.md`](references/sessions.md).

### Documents — the fifth grammar (proposed)

Drive and Notion titles have no grammar yet: a census of 46 recent titles (2026-10-02)
found five separators, seven version marks and four date styles. What already follows from
this page: the client in full, never an abbreviation, in a title (one concept, one word); an
ISO date; one separator. *Judgment until ruled; nothing checks it.*

### Naming a thing well — the part with no check

1. **Name the job, not the domain.** `tighten-copy` beats `copy-style-system`: a
   name that reads as a verb phrase tells an agent when to reach for it.
2. **If the name needs "and", it is two things.** One job per unit, applied to
   names.
3. **Do not encode the client.** Client work is the *source*, never the content. It
   goes in `source:`.
4. **Do not encode a version.** Git is the version. There is no `-v2`.
5. **Prefer the name you would search for at 11pm**, not the one that classifies
   most tidily.
6. **One concept, one word — and write the word down.** Rules 1-5 govern a name in
   isolation; this one governs it against every name already in the tree. A second
   word for a concept you already named is a retrieval failure, not a style
   quibble: the next reader searches the right idea with the wrong string and
   concludes it does not exist. Keep the vocabulary in a `glossary.yml` your checker
   reads, where a ruling is a check rather than a paragraph.
   Rubric and the false-positive classes:
   [`references/vocabulary.md`](references/vocabulary.md).
7. **A slot that predicts goes stale; a slot that observes needs a re-reader.** A name
   is written once, so every slot describes the moment of naming. That is fine for
   what never changes (the job, the kind of work) and wrong for anything the reader
   needs to know *now*. If the name must carry current state, give that state its own
   slot and a mechanism that re-sets it. Otherwise leave state out of the name.
   **Verified 2026-09-29:** a session's number was a prediction ("will this matter?"),
   51 of 57 sessions predicted yes, and the list stopped separating anything. The
   fix was an observed `STATUS_` slot re-read on every sweep. A stale device tag on a
   branch is the same failure; see the fourth grammar above.

## 3. Frontmatter

One rule you can hold in your head: **`created:` + `source:` on everything.**
`created:` is the authoring date; `source:` is where it came from. `extracted:` said
the second thing twice and is retired.

The per-library field tables are in
[`references/CHEATSHEET.md`](references/CHEATSHEET.md). Keep yours **generated from
the same schema file the linter reads**, so the documentation cannot disagree with the
checker.

**An unknown field is blocked.** This is the check that matters most, because the
failure mode was not disagreement — it was invention. Seven fields appeared in
the skill library that no convention had ever declared: `user-invocable:` ×3,
`triggers:` ×2, and `type:`/`tags:`/`category:`/`metadata:` once each. Each one
looked like a convention to the next session that read it. Adding a field should be a
deliberate edit to the schema.

Writing that check forced a ruling on each, and two of the seven were **kept**
(`user-invocable`, `metadata`). The per-field rulings and the lesson:
[`references/field-rulings.md`](references/field-rulings.md).

*Judgment:* whether a `source:` is true, and whether a `description:` actually fires.
Both are well-formed when fabricated.

## 4. How it is invoked

Short form for quick calls, a fenced block when the detail matters. Same grammar
either way. The shape, the frontmatter declaration, full spec and worked examples:
[`references/invocation.md`](references/invocation.md). Its runtime counterpart — how a unit
asks for a slot it could not resolve, without a model authoring the options — is
[`references/asking.md`](references/asking.md). Check the contract
with your linter, and an emitter with a menu driver's `--validate <emitter>`.

Three rules carry the weight:

1. **A missing required slot stops the run.** Ask, never assume. This is the
   prompt library's intake-gate rule generalized: a session that starts on assumed
   defaults produces confident nonsense, and you pay for it at review time.
2. **A slot is never both required and optional.** Blocked — that is the ambiguity
   that makes an agent guess.
3. **Do not pass the same slot twice.** A flag and a block key naming one slot is an
   error, not a precedence puzzle. Nobody should have to remember which wins.

*Checkable:* the contract's shape — kebab tokens, disjoint slots, known keys.
*Judgment:* whether the declared slots are the ones the body actually reads. A skill
can declare `required: [url]`, ignore it, and pass clean.

## 5. Maintaining it when you are not watching

Four tiers, by failure class. The split is the whole design: the tier that needs no
attention handles the drift that actually happens.

| Tier | What holds it | Catches |
|---|---|---|
| **Generate** | a generator rebuilds from frontmatter | README indexes, `MANIFEST.yml`, the cheat sheet's own tables |
| **Block** | pre-commit, block tier only, touched units only | names, missing/retired/unknown fields, dates, enums, intake shape |
| **Report** | a weekly digest | staleness, over-long descriptions, unmigrated invocations, unhooked clones |
| **Settle** | a vocabulary check against `glossary.yml` + a ruling from you | one concept named two ways — the only tier whose findings a machine cannot decide alone |

A workable tool shape: `lint <library> [--tier block|report]`, `apply <library>` (dry run by
default, `--apply` to normalize + regenerate), an `install-hook` that wires the block tier into
pre-commit, a `verify` that is the gate for the tooling itself, and for the settle tier a term
extractor piped into a vocabulary checker that proposes and never applies.

**Why generate rather than document** (the six skills a prose rule let fall out of the
index), and **where the enforcement is genuinely thin** — the block-tier hook, worktree
hooks, `--no-verify`, a report tier that never applies:
[`references/enforcement.md`](references/enforcement.md). Read it before wiring a
pre-commit hook.

## The `audit` verb

`intake.verbs` has declared `audit` since this skill was written, and for a while
nothing said what it did — the exact defect §4 warns about, sitting in this page's
own frontmatter.

```
/naming audit
/naming audit --library skill-library
```

It runs the settle tier and hands you the candidates: extract every term on a
controlled surface, cluster the same-surface pairs, check them against the
glossary, and present what is left. Then you adjudicate, using
[`references/vocabulary.md`](references/vocabulary.md) — that is the whole job, and
the reason this verb cannot be a script. `--library` narrows the scan; omitted, it
reads all four.

It proposes and never applies. Accepting a ruling means writing a row into
`glossary.yml`; nothing renames a file on your behalf.

## Gotchas

1. **A convention with no generator or check is a wish.** Every rule in this skill had
   already been written down in a CLAUDE.md somewhere. They drifted anyway. The delta is not
   better prose — it is a schema file plus a hook.
2. **Never let a script infer which renames are safe.** A normalizer that derived its
   mechanical-rename set from the retired-field descriptions concluded
   `triggers: -> description:`, and would have overwritten two skills' trigger lists with a
   duplicate key. Enumerate the safe set explicitly.
3. **A rewrite must check its target key is free.** Even inside the safe set — a file
   holding both `extracted:` and `created:` is exactly the file a blind rename damages.
4. **Exemptions carry a stated reason and are audited.** Each exempt path (a vendored mirror,
   a shared asset pack, a generated-data dir) gets a sentence saying why in the schema, and
   `verify` fails on an exemption whose path no longer exists. A pattern-matched escape hatch
   is how this rots quietly.
5. **`status:` is an enum and was carrying prose.** One routine had
   `status: working — validated on <client>…` while its `MANIFEST.yml` claimed a `verify:`
   field the entry doc did not have. Two files disagreeing about whether a routine had a gate
   is the exact class that generating the manifest removes.
6. **An entry doc with no frontmatter is silent.** Every hand-run census of one library
   counted four routines instead of five because one `ROUTINE.md` had no frontmatter. A
   missing file is loud; a file with no frontmatter is not.
7. **Renames leave orphaned symlinks.** Renaming a skill strands its
   `~/.claude/skills/` link. After any rename:
   `find -L ~/.claude/skills -maxdepth 1 -type l -print -delete`.
8–11. **Cron-harness gotchas** — a double hyphen breaks a plist's XML comment; a cron
   harness must not reference a worktree path; a cron that writes into a repo owns the
   commit; ship the wrapper with the plist:
   [`references/cron-gotchas.md`](references/cron-gotchas.md).
12. **A new prefix shaped like an existing slot must be parsed first, everywhere.**
   `DEL_`, then `YOU_` and `AGT_`, are three capitals and `_`, which is exactly a tag.
   Any checker that tests the tag regex first reads `YOU_014_BLD_x` as tag `YOU`, loses
   the number, and "repairs" the rest. **Verified 2026-09-29:** a session reaper resolved no
   registry row for a `YOU_014_…` fixture until it stripped the status first. When you
   add a slot, grep for every parser of the grammar, not just the one you are editing.

## Receipts

**Verified** 2026-08-17 and 2026-08-21 — what was run, and against what:
[`references/receipts.md`](references/receipts.md).

**Unverified:** that a weekly report job behaves the same on a schedule as by hand. Load it
and fire it with `launchctl start` before trusting it: `launchd` gives a job no
`SSH_AUTH_SOCK` and a different `PATH`, and testing in a friendly shell proves nothing about
that.
