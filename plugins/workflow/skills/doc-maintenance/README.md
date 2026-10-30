# doc-maintenance

A weekly sweep of your operational docs for dead loops, stale paths, index drift and failing
schedulers. It files each finding as a review card. It never edits a doc.

## When to use it

- **Weekly**: run it on a schedule to catch rot before a fresh session trusts it.
- **"Are the docs stale?"**: you suspect a loop ended but its doc still reads as live.
- **After a move or rename**: cards and skills may still cite old paths.

Not for skill overlap or bloat (use `learn` audit) and not for knowledge-vault health (use that vault's linter).

## How to use it

```
/workflow:doc-maintenance
```

It takes no arguments and does one bounded sweep per run. You can also ask in plain words,
e.g. *"sweep the docs"* or *"doc maintenance."*

The skill then runs five checks:

1. **Dead loops**: `*STATE*.md` files not marked `[CLOSED]` and older than 7 days, or docs
   describing a recurring loop with no live scheduler.
2. **Stale paths**: absolute and `~` paths in commands, `SKILL.md` files and STATE files that no longer exist.
3. **Index drift**: a README or manifest table that disagrees with the directory it indexes.
4. **Scheduler liveness**: `launchctl list` against LaunchAgent plists, for non-zero exits, unloaded plists and missing runner scripts.
5. **Review-queue drift**: uncommitted cards in the review queue repo.

Then it stages one card per distinct finding, skipping any already open. Mechanical hygiene
findings can share one housekeeping card.

## Example

A STATE file for a loop that ended three weeks ago has no `[CLOSED]` marker. The sweep stages
one card saying the doc presents a dead loop as live, with the file path and its age.

## What you get

- **Review cards**: one per finding, with `approved: false`, as files or issues on your own backlog.
- **A summary**: N findings, M new cards, K skipped as already open, and the single highest-leverage item.
- **A one-line result** when everything is clean.

It never edits, deletes or fixes a doc. The one exception is when you approve a card live and say "apply it".

## Requirements

- **`git`**: for the review-queue check.
- **`launchctl`**: macOS, for the scheduler check.
- **A review queue**: a repo of cards or an issue backlog. Card rules come from the `learn` skill.
- No scripts, env vars or MCP connectors.
