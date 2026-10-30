# wrap

Close out a session properly: review what you touched, route learnings, turn follow-ups into issues, leave nothing in progress, and write the handoff.

## When to use it

- **End of a session**: you are done and want state a fresh agent can pick up.
- **End of a loop pass**: an autonomous agent run is finishing.
- **Draft PRs parked**: you opened PRs this session and want each one resolved.

Not for a mid-session checkpoint. For a research-only session that touched no code and no issues, only the learn and handoff steps apply.

## How to use it

```
/workflow:wrap
```

In plain words: *"wrap up"*, *"close out the session"*, *"end of session"*. To let it merge, say so in the same message, e.g. *"wrap up and merge anything you can."* Merging is never inferred.

The skill then runs five steps in order:

1. **Review**: inventories every repo the session wrote to, checks nothing is already merged, reviews the diff, fixes small findings, and confirms findings on merged PRs actually landed.
2. **Learnings**: runs the `learn` routing and patches stale prompts, skills, or templates the session proved wrong.
3. **Follow-ups**: opens one GitHub issue per real follow-up, each with a done-means, and leaves state comments for the next agent.
4. **In Progress is empty**: every card or issue this session owns moves to To Do, Blocked, or Done.
5. **Handoff**: writes the durable handoff and a short self-review last, so it matches final state.

Every PR the session opened ends in one of three states: ready for review, still draft with a stated question to the user, or closed with a reason.

## Example

A session opens two PRs. Wrap finds one draft, runs checks, flips it ready, comments on the other with the decision needed, opens an issue for a deferred fix, and writes the handoff.

## What you get

- A terse report: draft and check results, review verdict, artifacts written, issues and PRs with URLs, handoff location, and a worktree verdict as text.
- Line 1 of the report is a status word: `DONE`, `PARTIAL`, `BLOCKED`, or `FAILED`.
- It will not merge by default, remove worktrees, or claim gated edits are live.

## Scripts

Optional second-model check of the status word. Without `JUDGE_CMD` it exits 3 and changes nothing.

```
bin/wrap_status.sh [--transcript PATH] <draft-report-file>
```
Finds the session transcript, runs the pipeline, prints verdict JSON, and saves it. Exit 0 consistent, 1 overclaim, 3 no judge, 2 bad input.

```
bin/wrap_evidence.py <transcript.jsonl> [--no-git] [--no-gh] > evidence.json
```
Collects the user's asks and git/gh facts for the session. No writes.

```
bin/wrap_evidence.py <transcript.jsonl> | bin/wrap_verdict.py [--report FILE] [--log FILE|--no-log]
```
Compares your claimed status to the computed one.

## Requirements

- **CLIs**: `git`, `gh`, `python3`. The ready-but-red check uses the `unstick-prs` skill's `prr.sh`.
- **Env vars** (optional): `JUDGE_CMD`, `WRAP_VERDICT_MODE` (`shadow` by default), `WRAP_PROJECTS_DIR`, `CLAUDE_CODE_SESSION_ID` (set by the harness).
- **MCP connectors**: none.
