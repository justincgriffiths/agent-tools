# shape-an-idea

Turn an idea that is clearly worth doing, but not yet specified, into work a cheaper agent can
run without asking a question.

## When to use it

- **Parked ideas**: an issue says what and why, but leaves how, in what pieces and by whom open.
- **Delegating to agents**: you want packages sized for a model tier, not one big vague task.
- **Specs that misfire**: a spec read clearly to its author but sent a smaller model the wrong way.

Not for raw notions with no evidence they matter (talk first), work already split into packages
a mid-tier agent can run (just dispatch it), or stress-testing a finished plan.

## How to use it

```
/workflow:shape-an-idea owner/repo#123
/workflow:shape-an-idea owner/repo#123 autopilot
```

Pass an idea or an issue reference. Add `autopilot` to let the agent answer its own questions.
Plain words work too, e.g. *"shape this idea"* or *"turn this issue into delegable work."* Plan
on 30 to 60 minutes.

The skill then:

1. Creates one idea doc (`docs/ideas/<slug>.md` unless you name a place) before the first
   question, so you can watch it fill in.
2. Reads the issue, its comments and linked issues, and carries over what is already settled.
3. Interviews you in quick picker rounds, with a recommended answer on every question.
4. Plans research on the assumptions that would kill the idea, then runs it in parallel with
   sub-agents.
5. Splits the work into deliverables, work packages (each with a tier and an acceptance check)
   and a timeline.
6. Proves the spec: hands the package most likely to be misread to an agent on its assigned
   tier, with only the package text.
7. With your go-ahead, writes a parent issue and one child issue per package.

## Modes

- **Interactive** (default): you answer every round.
- **Autopilot**: the agent answers from evidence, logs each answer as `agent (assumed)`, and
  stops only at gates. You then review the whole log in one round and the overturn rate is
  recorded.

Gates are yours in both modes: who it is for, money, anything client-facing or irreversible,
and any low-confidence decision.

## Example

An issue says "add a weekly usage report" and lists four "child to open" lines. You run the
skill on it. You confirm the audience and cadence in two rounds. It ends with five packages
tiered `script`, `small` and `mid`, a dated timeline, and one package dry-fired on a cheaper
agent.

## What you get

- **Idea doc**: problem statement, decision log, assumptions, research, deliverables, work
  packages, dry-fire result.
- **Issues**: a parent plus one child per package, only after you confirm.
- **Not included**: a recommendation on whether to do the work. That stays with you.

## Scripts

Check that the doc clears the bar. It prints one line per gap and exits 0 when complete:

```
python3 plugins/workflow/skills/shape-an-idea/bin/idea-doc-check.py docs/ideas/<slug>.md
```

Pass `-` instead of a path to read from stdin. Exit 1 means a gap, 2 means a usage error.

## Requirements

- **python3**: for the doc check.
- **Issue access**: a way to read and write issues (such as `gh`) if you shape from an issue or
  publish.
- No API keys.
