# The intake grammar

How to pass information into a command, once, consistently. The problem it solves:
seven skills declared `argument-hint:` and used **five different grammars** between
them, so every invocation was a small act of recall.

```
argument-hint: "[--scan <canonical> <vendored>] | [--vendor <family>] | [--apply <report>]"
argument-hint: "(no args — one bounded sweep per invocation)"
argument-hint: "[audit] — bare = capture this session's learnings; 'audit' = sweep"
argument-hint: "--new <name>|--edit <route>|--list · --client <slug>|--operators · [--template <name>]"
argument-hint: "<topic> [intent] — e.g. 'markets daily', 'security weekly', 'product pov'"
argument-hint: "[pull|push|weekly] — bare = weekly (full cycle)"
argument-hint: "[ABC-xx | XYZ-xx] — bare = query the board and propose candidates"
```

Flags, pipe-alternatives, dot-separated groups, bare subcommands with prose glosses,
positional-plus-examples. All reasonable in isolation. Together they are a language
with seven dialects, and the cost lands on you at the moment of use.

## The shape

```
/<unit> [<verb>] [--flag value ...]
```

optionally followed by a fenced block:

````
/<unit> <verb>
```intake
slot: value
slot: value
```
````

One grammar. The block is not a different mode — it is the same slots, written where
there is room to write them.

## Rules

**Verb** — the first bare token, kebab-case, drawn from the declared `verbs:` list.
Omit it when the unit declares no verbs. Never more than one.

**Flags** — `--kebab-case`, value as the next token or `--flag=value`. A boolean flag
takes no value; its presence is the value. Lists are comma-separated with no spaces
after the comma: `--surfaces /,/pricing,/demo`.

**Block slots** — `slot: value`, one per line, kebab-case slot names, aligned for
reading. Everything after the first colon is the value, colons included, so a URL or
a sentence needs no quoting. A blank line ends nothing; the fence does.

**Multi-line values** — indent the continuation. Use this for the one thing that
matters most and that a flag cannot carry: context in your own words.

````
```intake
url:      acme.com
context:  Client thinks the pricing page is the problem. I think it is the
          nav — three sessions of heatmaps point at the second click, not
          the first. Test both, tell me which.
```
````

**Three hard rules:**

1. **A missing required slot stops the run.** The agent asks. It does not assume a
   default, and it does not start work "to see how far it gets". This is the
   prompt library's intake-gate rule generalized — a run that begins on assumed
   defaults produces something confidently wrong, and you find out at review.
2. **A slot is never both required and optional.** Blocked by the checker.
3. **Never pass the same slot twice.** A flag and a block key naming the same slot is
   an error, not a precedence puzzle. There is no rule to remember because there is
   no collision permitted.

## Declaring the contract

In the unit's frontmatter, so it is machine-readable and checkable:

```yaml
intake:
  verbs:    [scan, estate, rerender]
  required: [url]
  optional: [surfaces, viewport, deliverable, known-issue, context]
  defaults:
    viewport: desktop+mobile
```

`verbs:` omitted means the unit takes none. `defaults:` may only name slots the
contract declares. All four keys optional; the block itself is optional — a unit with
no arguments declares no `intake:`.

A linter can check the shape: known keys, kebab tokens, disjoint required/optional,
defaults ⊆ declared slots. It cannot check that the body reads the slots it declares.
That one is on you.

## Worked examples

**No arguments.** `doc-maintenance` — one bounded sweep, nothing to pass. Declares no
`intake:`. The old `argument-hint: "(no args — …)"` was prose explaining an absence;
absence needs no prose.

```
/doc-maintenance
```

**Verb only.** Was `[pull|push|weekly] — bare = weekly (full cycle)`.

```yaml
intake:
  verbs: [pull, push, weekly]
  defaults:
    verb: weekly
```

```
/skills-central-sync            # weekly, per defaults
/skills-central-sync pull
```

**Verb plus one required slot.** Was `[ABC-xx | XYZ-xx] — bare = query the board…`.
The bare form is a *different job* (propose candidates) from the specified form (spec
this card), so it gets its own verb rather than living in a default.

```yaml
intake:
  verbs:    [spec, propose]
  optional: [card]
  defaults:
    verb: propose
```

```
/plan-card                      # propose candidates
/plan-card spec --card ABC-297
```

**Rich, where the block earns its place.** Was the dot-separated
`--new <name>|--edit <route>|--list · --client <slug>|--operators · [--template …]` —
three flag *groups* separated by a middle dot that meant "and also pick one from
here", a grammar you had to have read before to parse.

```yaml
intake:
  verbs:    [new, edit, list]
  required: [surface]
  optional: [route, client, template, flag, context]
```

````
/portal-page new
```intake
surface:  client-hub
client:   acme
route:    /insights
template: module-4point
context:  Third tab, next to Reports. Same guard as Reports — do not make
          it public.
```
````

The middle dots are gone, the groups are named slots, and the checker can tell you
that `surface:` is missing before anything runs.

## Migration

`argument-hint:` stays a legal optional field: it is the human-facing gloss, and a
`/`-menu shows it. But a unit with an `argument-hint:` and no `intake:` is a
**report-tier finding** — the hint is prose an agent has to re-parse, which is the
original problem.

When this grammar was adopted, seven units were in that state. They are not worth a
rewrite pass on their own; convert each one the next time you touch it, and let the
linter's report tier (a weekly digest) keep the list in front of you.

## What this does not solve

- **It does not make the slots the right slots.** A contract can be well-formed,
  fully checked, and ask for the wrong five things.
- **It does not stop a body ignoring its own contract.** Declare `required: [url]`,
  never read it, pass clean.
- **It does not help with the thing you did not think to say.** The `context:` slot
  exists because free prose is the highest-value input and the least structurable.
  Nothing checks it and nothing can.
