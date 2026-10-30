# write-work-items

Turn a pile of tasks into two things: a few **parent items** a human can scan in a minute, and
the **child items** an agent can execute without asking questions.

## When to use it

- **Before queueing work**: you're about to hand a batch of tasks to an agent loop or a backlog.
- **Opaque task lists**: someone reads your list and says "this means very little to me."
- **Busywork smell**: ten items that are really three things, or items with no reason attached.

Not for speccing one item in depth. This skill sets the levels across a *set* of items.

## How to use it

```
/workflow:write-work-items
```

Run it in a session that already has the work in view, such as an audit you just finished, a
list of follow-ups, or a handoff. You can also ask in plain words, e.g. *"write these up as work
items before we queue them."*

The skill then:

1. Lists the items you were about to write, without writing them yet.
2. Groups them into 2–4 real things by shared cause or outcome, not by repo or file type.
3. Writes each **parent**: a plain-words title, what we're doing in concrete nouns, why it
   matters, and a done-means you can check in 60 seconds.
4. Writes each **child**: the exact change, what to verify first, what not to touch, and what
   done looks like. One fire, one reviewable outcome.
5. Stamps every item with `source:` and `why:`, and flags anything expensive (merges, deploys,
   prod, secrets) as a human gate.

## Example

Nineteen agent-queue items that all say "append the block to CLAUDE.md in repo X" become:

| Parent (you read this) | Children (the agent runs these) |
|---|---|
| Delete the retired-workflow mandate from the app and infra repos' instructions; the tool it orders agents to run no longer exists | One child per repo: remove the section, verify nothing else references it |

## What you get

Parent and child text you can paste into GitHub issues, a card board, or a file-based queue.
The skill does not create the issues itself.

## Requirements

None. The skill is pure judgment, with no scripts and no credentials.
