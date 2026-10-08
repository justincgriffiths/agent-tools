# Branches and worktrees — the device tag

Detail behind the third grammar in `SKILL.md` §2. Units are invoked, records are
sorted, **branches and worktrees are places work physically happens** — which is
why they get a naming element the other two do not.

**New as of 2026-09-18, and deliberately so.** The source library had never had
device-named branches or worktrees. What it had was a `host/` namespace that named no host (see
*Prior art* below). This is a trial of the opposite, and it is worth trying
because a device tag is the **first naming element in this house that a machine
can check** — `scutil --get LocalHostName` either agrees with the tag or it does
not. Every other rule on this page is judgment a checker can only approximate.

## The grammar

```
<type>/<slug>[-<device>]
```

`type` is the change, from the set git convention already uses: `feat` · `fix` ·
`chore` · `docs` · `plan` · `spike`.

`device` is a name from a device registry you keep (e.g. a `devices.yaml`), lowercased.
An example (fictional) registry:

| Slug | Device | Kind |
|---|---|---|
| `devbox` | Devbox | laptop — primary workstation |
| `laptop2` | Laptop 2 | desktop mini — always-on compute, owns stateful jobs |
| `homeserver` | Home server | NAS — production runtime |
| `phone` | Phone | phone — mobile surface |

Canonical name only. Never the hostname (`dana-mac-mini`), never a former name,
never the kind (`mini`, `air`, `nas`). One vocabulary, published by the registry —
so the tag is checkable against a closed set rather than spell-checked by eye.

```
feat/deletion-lane-laptop2     the reaper; runs on the mini, nowhere else
fix/photo-import-devbox        Full Disk Access — reproducible only on the laptop
chore/search-index-homeserver  a container config change on the NAS
feat/branch-worktree-naming    a skill edit; every host runs it identically
```

## When the device is relevant

The test is **falsifiability, not topic**: would this branch behave differently,
or be unverifiable, on another machine? If yes, tag it.

Four conditions, any one of which earns a tag:

- **Scheduled** — it touches a plist, or a job declared with a `hosts:` field in
  your schedule registry.
- **Stateful** — it writes per-host state that is never shared (a state dir, a
  ledger, a cursor, a lock), so exactly one host may own it.
- **Credentialed** — it can only be exercised where a credential dir, a mounted
  volume or a TCC grant exists.
- **Physical** — it is a worktree. A worktree is a directory on one machine, so
  the device is always relevant. **Worktrees are tagged without exception.**

Leave it off when the work is host-neutral — a skill, a doc, library code, anything
where "it worked on my machine" is not a meaningful sentence. An omitted tag is
itself a claim: *this runs anywhere*. Omitting it carelessly is as wrong as tagging
carelessly.

## Why the tag goes in the slug, not the namespace

A namespace is a category. Putting the device there says a branch *belongs to* a
machine, which invites a permanent per-machine line of development — and that is
the thing that actually bit. The slug is a description, and a device in the slug
says only *this is where the work runs*, which is true and stays true.

### Prior art — what `host/` actually got wrong

`host/mail-reaper` and `host/move-drain-to-mini` in one data-migration repo are the closest
thing to precedent, and they are **not** an argument against device tags — neither
one names a device. `host/mail-reaper` names a feature; `host/move-drain-to-mini`
names a *change* that happens to mention a machine. The namespace announced
"per-host branch" and then withheld which host.

The cost, 2026-09-17: the mini was checked out on `host/move-drain-to-mini` while
running `host/mail-reaper`'s code. Two readers independently grepped the
laptop's checkout for a `reap` subcommand, found zero matches, and concluded the feature had
been lost in a merge. It existed, one commit away, on the other machine. A truthful
device tag is exactly the thing that would have made that visible on sight.

## A stale tag is worse than no tag

The tag is read as fact, so it has to be one. Two rules:

1. **Rename or delete when the work moves.** If a lane moves from the laptop to the
   mini, the branch name moves with it.
2. **Tag the device the work RUNS on, not the one you typed it on.** You will
   author `-homeserver` branches from the laptop constantly. The tag names the target.

## Lifecycle — a separate rule, and the one that actually bit

A device tag does not make a branch permanent. **Every branch still merges to
`main` and is then deleted.** Convergence is independent of naming, and conflating
the two is what left that repo's `main` 72 commits behind with every line of
working code on a side branch:

- One `main`. Hosts run it detached and pull.
- A device tag says where work is *proven*, never where it *lives forever*.
- A branch with no merge and no deletion is drift regardless of its name.

## Worktrees

```
<worktrees-root>/<slug>-<device>
```

Same grammar, no type prefix — the directory already sits under `worktrees/` and
the enclosing repo already supplies the project. The device is **mandatory**: the
path is physical, and two machines can otherwise hold identically-named worktrees
containing different work.

```
.claude/worktrees/photo-stall-devbox
.claude/worktrees/deletion-lane-laptop2
```

**One root per repo.** A skill library with a few dozen worktrees split across two
parents — `<repo>/.claude/worktrees/` and a separate `<worktrees>/<repo>/` — leaves
`git worktree list` as the only way to find one and neither location is
authoritative by inspection. Pick `.claude/worktrees/` (the harness default) and
treat anything outside it as drift, with the standing exception of the main-pinned
`live` checkout that a PR-sweep script freshens.

**Read the base ref before trusting a worktree.** `worktree.baseRef` is `fresh`, so
a new worktree branches from the remote default — correct when that remote is, and
a trap when it is not. **Verified 2026-09-18:** in one repo, `origin` was a
deprecated remote sitting 62 commits behind the real one; a worktree cut there
came up missing the entire `skills/naming/` directory, and editing it blind would
have merged as a 62-commit regression. Check `git rev-list --left-right --count
<real-remote>/main...HEAD` before the first edit, every time.

## Enforcement

What is checkable, and therefore what should be checked:

- **Vocabulary** — a tag, if present, is a name in `devices.yaml`. An invented or
  misspelled device is a hard failure; this is a closed set.
- **Truth** — on a tagged branch, compare the tag against `scutil --get
  LocalHostName` and warn on a mismatch that is not an authoring case. This is the
  check no other naming rule can have, and it is the reason to adopt the tag.
- **Namespace** — reject any branch whose first path segment is a device name, and
  reject `host/**`. The device is a tag, not a category.
- **Convergence** — flag a branch whose merge-base with `main` has not moved in N
  days. Naming was never the real defect; this is.

Judgment stays here; the checks belong in your naming linter, beside
the existing kebab-case and entry-doc rules.
