# The asking contract

`invocation.md` covers how information gets *passed in*. This covers what happens when it
wasn't — when a required slot is missing and the unit has to ask.

The intake grammar's first hard rule already says what to do: *a missing required slot stops
the run; the agent asks; it does not assume a default.* It does not say **how** to ask, and
left open that turns into the same drift the grammar was written to kill — options typed into
SKILL.md prose, going stale against the data they describe, then translated by hand into a
command that may be wrong.

## The shape

The unit does not compose the question. A **menu emitter** — any command the unit names —
writes one JSON object to stdout:

```json
{
  "kind": "menu",
  "question": "Which account do you want to be?",
  "header": "Account",
  "multiSelect": false,
  "options": [
    { "key":         "acme",
      "label":       "acme",
      "consequence": "Acme (fulltime) · sam@acme.com — active here now",
      "recommended": true,
      "command":     "me.sh use acme" }
  ]
}
```

Field names are `key` · `label` · `consequence` · `recommended`, plus `command`. Use one
vocabulary for options-as-data across the whole library, not two.

## The loop

A **driver** — a small `menu.sh` at a terminal, or a `/menu` command in a session — runs exactly this:

1. Run the command. Capture stdout.
2. Parses as JSON with `kind == "menu"`? Present the options, take the chosen option's
   `command` **verbatim**, go to 1.
3. Otherwise stdout is the result. Show it. Stop.

Chaining is owned by the scripts: a command may emit the next menu. So a multi-step flow is a
state machine whose transitions are commands, and the model is a renderer rather than a
participant. It reads four strings and reports which was picked. That is the one job it cannot
get wrong.

## Rules

**Emitters**

1. **Two to four options.** The binding constraint — `AskUserQuestion` takes no more. An
   emitter with more choices paginates: the fourth option is `More…`, whose `command` re-emits
   the next page.
2. **`label` one to five words; `header` twelve characters or fewer.** They render as a chip
   and a tag; longer is truncated, not wrapped.
3. **Never emit an "Other" option.** The tool adds one. A second is noise.
4. **`consequence` says what happens if chosen**, not what the thing is. "switches this repo
   and warms 1Password" beats "the Acme account".
5. **Exactly one option carries `recommended: true`.** Propose, don't quiz.
6. **`multiSelect: true`** means the driver runs the chosen commands in order.
7. **Emitted order is the emitter's.** A driver renders options in the order given and never
   sorts the recommendation to the top. `AskUserQuestion`'s own convention prefers
   recommendation-first, and it is wrong for a fixed roster: the three accounts should sit in
   the same order every time so the choice becomes muscle memory, while which one is
   recommended changes with the directory. Drivers mark the recommendation by appending
   ` (Recommended)` to its label instead.
8. **The driver executes `command` through the shell, verbatim.** Point a driver only at
   emitters you control, and never build a `command` from untrusted input.

**Units**

7. **Never ask what you can resolve.** A question you could have answered from the data is a
   worse interruption than a flag. The picker is for a slot that is genuinely ambiguous, or for
   an invocation that explicitly means "let me choose". When the value *is* resolvable, still
   offer it — but mark it `recommended` and say so in the `consequence`.
8. **A menu answer is not authorization.** A guard that requires typed approval reads the
   *prompt*; an `AskUserQuestion` answer issues no token and grants nothing. No option may be the sole approval for a guarded
   write. Where one would be, the `consequence` names the phrase that has to be typed.
9. **The unit names the emitter; it does not restate the options.** The moment a SKILL.md lists
   the choices, there are two sources of truth and one of them is already wrong.

## Naming the emitter

Name it in the unit's body, next to the slot it fills — not in frontmatter.

An earlier draft added an `asks:` key to the `intake:` block, mapping a slot to its emitter.
Two reasons it is not here. A simple linter's intake reader is a flat line scanner: a nested
map registers *both* `asks` and the slot beneath it as top-level intake keys, so the block
would BLOCK on an unknown-key check. And nothing consumes the binding — it was machine
readability invented before anything needed to read it.

So: `intake:` declares the slots; prose names the emitter that fills one.

Enforcement splits the same way. The linter validates
the `intake:` shape — unknown keys, inline-list form, kebab tokens, and the disjointness of
`required` and `optional`. A driver's `menu.sh --validate <emitter>` validates an emitter
against rules 1–8 above, and the drivers refuse to render a menu that breaks them.

## Worked example

A `switch-accounts` unit declares `optional: [persona, surface]` and names `me.sh menu`
as the emitter in its front-door section. `persona` is optional, not required, because the
script resolves it from the working directory — rule 7 again. Typed bare,
`me.sh` resolves the persona from the working directory and says nothing. Typed as `/me`, the
emitter runs: four options, the current persona marked `recommended` with *"active here now"*,
the others carrying live probe output — *"needs re-auth: op, gmail"*, *"gh not logged in —
switch will be partial"*. Pick one, the driver runs its `command`, and if the probe still
reports a stale surface that command emits a second menu listing only what is actually broken.

Nothing in that flow was authored by a model.
