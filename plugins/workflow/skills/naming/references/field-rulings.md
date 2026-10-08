# Frontmatter field rulings (2026-08-17)

Why each of the seven invented fields was kept or retired when the unknown-field check was
written. Context: `../SKILL.md` §3.

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
that does not is a preference.** Two of the seven did not survive, and finding that out
cost one lint run.
