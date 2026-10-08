---
name: naming
description: Decide what to CALL a thing and where it goes before creating it — a new skill/routine/template/prompt, a directory, a script, a frontmatter field, or a command invocation. Load BEFORE authoring, and when a name feels arbitrary, when two things want the same name, or when you are about to invent a frontmatter field. A reusable house grammar for a personal or team library of agent skills; the judgment is here, enforcement belongs in your own linter.
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
- Enforcement: a linter + generator you own, in three tiers (generate · block · report) — §5

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

*Checkable:* kebab-case on units and scripts, entry-doc presence, `name:` matching the
directory. *Judgment:* whether the name says what the thing is. `portal-page` and
`portal-home` both pass the checker; whether they are one skill is your call.

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

Writing that check forced a ruling on each, and two of the seven were **kept** —
which is the useful part of the exercise:

| Field | Ruling | Why |
|---|---|---|
| `user-invocable` | **kept** | Being invocable is orthogonal to taking arguments. The first draft retired it in favour of "an `intake:` block means invocable", which is plainly wrong: `doc-maintenance` is invocable and declares no intake because it takes none. |
| `metadata` | **kept** | `metadata.<harness>.{tags,related_skills}` is live config — a sync script copies these skills into a second agent harness, which reads it. Retiring it would have deleted working config with nowhere to put it. |
| `triggers` | retired → `description` | The description *is* the trigger. Where a trigger phrase was not already in the description, it was folded in — `deck-ship` kept "ship the deck" and "harvest the deck edits" that way. |
| `type` | retired | The library a thing lives in is its type. |
| `tags` | retired → `metadata.<harness>.tags` | One skill had top-level `tags:`; two used the nested form. The majority pattern won. |
| `category` | retired | Skills are flat. `category:` is a template field. |
| `canonized` | retired → `created` | A third name for the authoring date. |

The lesson worth keeping: **a rule that survives contact with the tree is a rule; one
that does not is a preference.** Two of my seven did not survive, and finding that out
cost one lint run.

*Judgment:* whether a `source:` is true, and whether a `description:` actually fires.
Both are well-formed when fabricated.

## 4. How it is invoked

Short form for quick calls, a fenced block when the detail matters. Same grammar
either way. Full spec and worked examples:
[`references/invocation.md`](references/invocation.md). Its runtime counterpart — how a unit
asks for a slot it could not resolve, without a model authoring the options — is
[`references/asking.md`](references/asking.md). Check the contract
with your linter, and an emitter with a menu driver's `--validate <emitter>`.

Short form — one line, up to about three slots:

```
/audit-landing-page scan --url acme.com --mobile
```

Rich form — same skill, same grammar, more detail:

````
/audit-landing-page scan
```intake
url:         acme.com
surfaces:    /, /pricing, /demo
viewport:    desktop+mobile
deliverable: deck
known-issue: hero CTA below fold on iPhone SE
```
````

Declared in frontmatter, so the contract is machine-readable and an agent knows what
to ask for **before** starting work:

```yaml
intake:
  verbs:    [scan, estate, rerender]
  required: [url]
  optional: [surfaces, viewport, deliverable, known-issue]
```

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

Three tiers, by failure class. The split is the whole design: the tier that needs no
attention handles the drift that actually happens.

| Tier | What holds it | Catches |
|---|---|---|
| **Generate** | a generator rebuilds from frontmatter | README indexes, `MANIFEST.yml`, the cheat sheet's own tables |
| **Block** | pre-commit, block tier only, touched units only | names, missing/retired/unknown fields, dates, enums, intake shape |
| **Report** | a weekly digest | staleness, over-long descriptions, unmigrated invocations, unhooked clones |

A workable tool shape: `lint <library> [--tier block|report]`, `apply <library>` (dry run by
default, `--apply` to normalize + regenerate), an `install-hook` that wires the block tier into
pre-commit, and a `verify` that is the gate for the tooling itself.

**The index drift is the argument for generating rather than documenting.** The skill
library's `README.md` had six skills missing under a CLAUDE.md rule that said to update the
index in the same commit as any skill change. The rule was prose, so it lost. Nothing was
generated, so nothing noticed. A prose-only rule is a draft.

**Where enforcement is genuinely thin — design for these up front:**

- **Worktrees break basename-based library detection.** A linter that derives library
  identity from the **basename** of the path it is given fails in a git worktree, because
  `git rev-parse --show-toplevel` returns the worktree path (`.../worktrees/<slug>`), not the
  library name. If the hook then treats any non-zero exit as a violation *while discarding
  stderr*, it blocks every commit with an empty reason. **Verified 2026-08-21:** a test
  commit from a worktree was blocked with a blank finding list. Two fixes: resolve the
  library by walking the path for the deepest component that names a known library; and have
  the hook distinguish exit 1 (violations — block) from exit 2 (lint could not run — warn and
  allow). Fail-closed with no message is worse than no gate.
- **An installer that skips linked worktrees** (`[ ! -d "$lib/.git" ]` — in a worktree `.git`
  is a file) reads as "worktrees are unprotected", but hooks live in the **common** git dir, so
  installing on the main checkout covers every worktree. The skip is misleading, not protective.
- **Hooks are per-clone and untracked**, so a fresh clone silently has no block tier. Have the
  report tier list unhooked clones.
- **`--no-verify` exists.** The digest should still surface what was bypassed — bypassing
  should cost a line in a report, not silence.
- **The report tier proposes and never applies.** It cannot fix a stale skill; it can only
  make sure you know.

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
8. **A double hyphen is illegal inside an XML comment**, so documenting a CLI flag in
   a launchd `.plist` header makes the plist unparseable. Hit twice in one skill —
   `--publish`, then `--refresh-state`. Both times **`launchctl load` accepted it and
   the job ran**, so nothing surfaced; `plistlib.load()` is what catches it. Write
   flags without the leading hyphens in plist prose, and parse-check before commit:
   `python3 -c "import plistlib;plistlib.load(open('x.plist','rb'))"`.
   A tolerant loader is not a validator — this is latent breakage on reboot.
9. **A cron harness must not reference a worktree path.** Live checkouts move. A plist
   whose `ProgramArguments` points into a worktree silently stops firing when that
   worktree is re-cut. Point at an installed copy of the wrapper
   (e.g. `~/Library/Application Support/<area>/`) or at the stable
   `~/.claude/skills/<skill>` symlink — and have the wrapper resolve the skill dir through a
   fallback list, so it fails loudly rather than half-running.
10. **A cron that writes files into a repo must own the commit.** Otherwise its
   output survives only when a human remembers, and the repo sits permanently
   dirty — which then masks real changes. Found the day a scheduled probe went
   live: it would have run four times a day forever, rewriting the same
   uncommitted report. If a cron may commit a generated file it solely owns, the
   obligation to actually commit it is the other half. Scope the commit to the exact path
   (`git commit -- reports/`) so it can never sweep up something hand-authored, and warn
   into the run log on a failed push rather than swallowing it.
11. **Shipping a plist whose wrapper does not exist fails silently, daily.** A plist named
   a wrapper script that was never written; `launchctl load` succeeds regardless, and the
   failure only shows as an empty log. If a plist names a wrapper, commit the wrapper in the
   same change, and have the wrapper write one heartbeat line to **stdout** — an empty
   launchd log is indistinguishable from a job that never fired.

## Receipts

**Verified 2026-08-17:** a linter, index generator, normalizer, and the generate-tier apply
(dry run and apply) were run against four libraries; the finding counts in this skill are
measured, not estimated.

**Verified 2026-08-21:** hook install then removal on a skill library; a worktree commit
blocked with an empty finding list and allowed again after removal; the linter exiting 2 on
a worktree basename; `plistlib.load()` rejecting a plist that `launchctl load` had accepted
and run; a launchd job firing on `launchctl start` and writing its heartbeat to both logs.

**Unverified:** that a weekly report job behaves the same on a schedule as by hand. Load it
and fire it with `launchctl start` before trusting it: `launchd` gives a job no
`SSH_AUTH_SOCK` and a different `PATH`, and testing in a friendly shell proves nothing about
that.
