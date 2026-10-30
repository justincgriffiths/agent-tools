# dedupe

Find out whether a directory is a copy of another one, which side is the real one, and which few files need a person to decide.

## When to use it

- **Suspected copy**: a directory in one repo mirrors another repo's.
- **Which is canonical**: nobody can say which of two trees is the source of truth.
- **Before committing**: a directory looks copied from somewhere and has no provenance stamp.

Not for stale links or dead paths (that is `doc-maintenance`), and not for overlapping skills (that is `learn` audit mode).

## How to use it

```
/workflow:dedupe
```

Name the two trees, or just the one you doubt. The skill asks for the rest with the question picker. In plain words: *"are these two directories the same?"* or *"which one is canonical?"*

The skill never guesses which tree is canonical. It always asks.

The skill then:

1. **Scans** (read-only): compares the canonical tree to the vendored copy and writes a report plus a verdict table.
2. **Sorts every file** into a verdict: `IDENTICAL`, `DRIFTED`, `ORPHAN`, `UPSTREAM-ONLY`, or `NESTED-REPO`.
3. **Hands you the review**: only `DRIFTED` and `ORPHAN` files need a decision. For each drifted file you pick `canonical`, `vendored`, or `both`.
4. **Syncs** once you have decided, using the family's existing copier if there is one, refusing while unresolved drift or orphans remain.
5. **Prevents** a repeat by adding a `VENDORED.yml` provenance stamp to the copy.

## Example

A repo carries a template folder copied from a master library. The scan reports 102 of 108 files identical, 6 drifted, none orphaned. You review 6 files, not 108.

## What you get

- `data/dedupe/YYYY-MM-DD-<family>.md`: the review report, led by how many files need your call.
- `data/dedupe/YYYY-MM-DD-<family>.tsv`: one verdict row per file.
- A one-line log entry per scan.
- It will not delete a vendored tree, resolve drift without you, delete a nested git repo, or commit an unstamped copy. The modified-time hint in the report is never the decision.

## Scripts

```
scripts/scan-tree.sh --canonical <dir> --vendored <dir> [--name <family>] [--out <dir>]
```
Read-only scan. `--name` labels the family in filenames. `--out` sets the report folder (default `./data/dedupe/`). Exits 0 even when it finds problems, 2 on bad usage or a missing directory. Appends to `scan-tree.log` beside the script.

## Requirements

- **CLIs**: `bash` and standard Unix tools. An existing sync script for the family, if you want to apply the result.
- **Env vars**: none.
- **MCP connectors**: none.
