# House grammar — cheat sheet

One page. Everything else is elsewhere: judgment in [`../SKILL.md`](../SKILL.md),
the invocation grammar in [`invocation.md`](invocation.md), enforcement in
whatever linter you pair it with.

The **field tables at the bottom are an example schema**. Generate yours from the same
schema file your linter reads, so they cannot drift from the checker. Everything above them is
hand-written and therefore suspect; if it disagrees with the tables, the tables win.

---

## Which library

| Library | Answers | The test |
|---|---|---|
| `skills/` | How should the agent *work*? | Remove the prose and the value is gone |
| `routines/` | What exact *steps* produce the artifact? | Same commands every time → script it |
| `templates/` | What does the *deliverable* look like? | The output shape is the artifact |
| `prompts/` | Can a *stranger session* do this from one paste? | Must work with none of your config |

## Naming, in full

**Everything is kebab-case.** Directories, scripts, frontmatter keys, intake slots,
verbs, flags.

| Shape | Means | Example |
|---|---|---|
| `kebab-case/` | a unit | `audit-landing-page/`, `deck-to-pdf/` |
| `_prefix` | **not a callable unit** — scaffold, staging, asset pack | `_shared/`, `_template-monthly.md`, `_epics/` |
| `-common` | shared asset pack, no entry doc | `research-common/` |
| `SCREAMING.md` | the canonical doc of its directory | `SKILL.md`, `MANIFEST.yml` |
| `snake_case/` | Python package — imports forbid hyphens | `my_slides/` |
| plural dir | a category | `contracts/`, `analyses/`, `audit-prompts/` |
| singular dir | a thing | `audit-full/`, `email-reconnect/` |

- Dates are ISO `yyyy-mm-dd`. Everywhere. Every field.
- No `-v2`. Git is the version.
- No client name in a name. Clients go in `source:`.
- If the name needs "and", it is two things.

## Unit layout

```
<library>/<unit>/                 skills, routines
<library>/<category>/<unit>/      templates
<library>/<category>/<unit>.md    prompts

  SKILL.md | ROUTINE.md | TEMPLATE.md      the entry doc — required
  scripts/                                 runnable
  references/                              lookup tables, reference-grade detail
  cron/                                    launchd plist + wrapper + scoped settings
```

## Frontmatter, in one line

**`created:` + `source:` on everything.** `created:` is the authoring date; `source:`
is where it came from. `extracted:` said the second thing twice — retired.

**An unknown field is blocked.** Seven were invented exactly once each
(`user-invocable`, `triggers`, `type`, `tags`, `category`, `metadata`, `canonized`).
Adding a field should be a deliberate edit to the schema.

## Invocation

````
/<unit> [<verb>] [--flag value ...]

/<unit> <verb>
```intake
slot: value
slot: value
```
````

- Missing required slot → **stop and ask**. Never assume a default.
- A slot is never both required and optional.
- Never pass the same slot twice — that is an error, not a precedence rule.
- Declare it: `intake: {verbs, required, optional, defaults}`.

Full spec, worked conversions of all seven legacy `argument-hint`s, and the migration
plan: [`invocation.md`](invocation.md).

## Tooling shape (build your own)

```
lint <library> [--tier block|report] [--show-exempt]   # findings; exit 1 = violations, 2 = could not run
apply <library> [--apply] [--only <stage>]             # dry run by default; normalize + regenerate
install-hook <library> [--apply]                       # wires the block tier; per-clone, untracked
verify                                                 # the gate for the tooling itself
```

## The three tiers

| Tier | Holds it | Needs you |
|---|---|---|
| **Generate** | indexes, manifests, these tables | never |
| **Block** | pre-commit, touched units only | at commit, with the fix named |
| **Report** | weekly digest | approval only |

**Thin spots, stated:** hooks are per-clone and untracked, so a fresh clone silently
has no block tier — the digest reports unhooked repos, and that is the only backstop.
`--no-verify` works; the digest still names what you bypassed.

## What no check catches

Whether the name is *right*. Whether a `description:` actually fires. Whether an
`intake:` matches what the body reads. Whether `source:` is true. Whether `created:`
is honest. Whether a generated index is *useful* — it will be current, complete, and
possibly a wall of truncated cells. Look at the rendered table.

---

# Field tables

<!-- BEGIN generated-schema-tables · do not hand-edit -->

### Prompt library (`prompts/`)

Unit path `<library>/<category>/<unit>.md` · entry doc **the .md file itself**

| Field | Required | Notes |
|---|---|---|
| `name` | **yes** |  |
| `description` | **yes** |  |
| `output` | **yes** |  |
| `evidence` | **yes** |  |
| `created` | **yes** | ISO `yyyy-mm-dd` |
| `source` | **yes** |  |
| `status` | **yes** | `draft` / `reviewed` / `live` |
| `summary` | no |  |
| `reviewed-by` | no |  |
| `first-run` | no |  |
| `second-run` | no |  |
| `updated` | no | ISO `yyyy-mm-dd` |
| `verified` | no | ISO `yyyy-mm-dd` |
| `intake` | no |  |

Retired here — blocked at commit:

| Retired | Use instead |
|---|---|
| `extracted` | created |
| `first_run` | first-run |
| `reviewed_by` | reviewed-by |
| `second_run` | second-run |

Soft limits (report tier): the .md file itself ≤ **400 lines**

### Routine library (`routines/`)

Unit path `<library>/<unit>/` · entry doc **ROUTINE.md**

| Field | Required | Notes |
|---|---|---|
| `name` | **yes** |  |
| `inputs` | **yes** |  |
| `outputs` | **yes** |  |
| `verify` | **yes** |  |
| `created` | **yes** | ISO `yyyy-mm-dd` |
| `source` | **yes** |  |
| `status` | **yes** | `draft` / `live` / `stub` |
| `summary` | no |  |
| `deps` | no |  |
| `optional-deps` | no |  |
| `intake` | no |  |
| `updated` | no | ISO `yyyy-mm-dd` |
| `verified` | no | ISO `yyyy-mm-dd` |
| `reviewed-by` | no |  |

Retired here — blocked at commit:

| Retired | Use instead |
|---|---|
| `brand` | (none — brand belongs to the template library) |
| `category` | (none) |
| `extracted` | created |

### Skill library (`skills/`)

Unit path `<library>/<unit>/` · entry doc **SKILL.md**

| Field | Required | Notes |
|---|---|---|
| `name` | **yes** |  |
| `description` | **yes** |  |
| `created` | **yes** | ISO `yyyy-mm-dd` |
| `source` | **yes** |  |
| `summary` | no |  |
| `group` | no |  |
| `intake` | no |  |
| `argument-hint` | no |  |
| `user-invocable` | no |  |
| `metadata` | no |  |
| `status` | no | `draft` / `live` / `deprecated` |
| `verified` | no | ISO `yyyy-mm-dd` |
| `updated` | no | ISO `yyyy-mm-dd` |
| `platforms` | no |  |
| `allowed-tools` | no |  |
| `delegates-to` | no |  |
| `reviewed-by` | no |  |
| `first-run` | no |  |
| `second-run` | no |  |

Retired here — blocked at commit:

| Retired | Use instead |
|---|---|
| `authored` | created |
| `canonized` | created |
| `category` | (none — skills are flat; category is a template field) |
| `extracted` | created |
| `first_run` | first-run |
| `reviewed_by` | reviewed-by |
| `second_run` | second-run |
| `source_repo` | source (name the work, not a local path) |
| `tags` | metadata.<harness>.tags (the majority pattern; top-level tags is a one-off) |
| `triggers` | description (the description IS the trigger) |
| `type` | (none — the library it lives in is its type) |

Soft limits (report tier): SKILL.md ≤ **300 lines** · `description` ≤ **60 words**

### Template library (`templates/`)

Unit path `<library>/<category>/<unit>/` · entry doc **TEMPLATE.md**

| Field | Required | Notes |
|---|---|---|
| `name` | **yes** |  |
| `category` | **yes** |  |
| `formats` | **yes** |  |
| `source` | **yes** |  |
| `created` | **yes** | ISO `yyyy-mm-dd` |
| `brand` | **yes** | `<brand-a>` / `<brand-b>` / `none` |
| `placeholders` | **yes** |  |
| `status` | **yes** | `draft` / `live` / `stub` |
| `summary` | no |  |
| `verified` | no | ISO `yyyy-mm-dd` |
| `updated` | no | ISO `yyyy-mm-dd` |
| `reviewed-by` | no |  |

Retired here — blocked at commit:

| Retired | Use instead |
|---|---|
| `extracted` | created |

<!-- END generated-schema-tables -->
