---
name: shape-an-idea
description: Turn a half-formed idea into three things in one sitting — a sharp problem statement, a research plan that actually gets run, and a rudimentary workflow you can try at N=1 tomorrow. Part interview, part coding session. Use for "help me flesh out this idea", "I have an idea for X", "is this worth building", "what would it take to automate Y", "shape this", "/shape-an-idea", or any vague ask where the person cannot yet say who it is for, what done looks like, or what the first step is. Owns the order of operations — decisions before research, research before workflow — and the line between facts (the agent finds them) and decisions (the person makes them). SKIP for a plan that is already specified (just build it), for pure stress-testing of a finished plan (a grilling skill), and for a research question with no idea attached (a research skill).
argument-hint: "the idea, in a sentence or a paragraph — rough is fine; anything missing gets asked"
intake:
  required: [idea]
  optional: [audience, deadline, constraints, prior-art, where-to-save]
created: 2026-10-12
source: extracted from the author's working sessions, 2026 — repeated sessions where an idea went straight to code, and the first real question ("who is this for?") surfaced three hours in.
summary: "Interview an idea into a problem statement, launch a research plan with sub-agents, and leave a rudimentary workflow proven at N=1"
group: "Capture & meta"
---

# shape-an-idea

An idea arrives as a sentence. What it needs before anyone builds it is three answers: **what
exactly is the problem**, **what do we not know yet**, and **what is the smallest thing we
could run tomorrow**. This skill gets all three in one session, in that order, and writes them
into one document the person can share.

**The failure this prevents:** going straight from the sentence to code. That happens because
building feels like progress and questions feel like delay. Three hours later the first real
question surfaces ("wait, who is this for?") and the code answers a different one.

---

## The one rule

> **Facts are the agent's job. Decisions are the person's.**

Never ask the person for something you could look up: what already exists in the repo, what a
tool supports, what a competitor charges. Dispatch a sub-agent and keep the conversation
moving. Never decide for them: who it is for, what "good" means, what to cut. Put each one to
them as a question, with your recommendation attached, and wait for the answer.

Everything below is how that rule plays out across the three acts.

---

## The artifact: one idea doc

Create it **before the first question**. A doc that starts empty and fills in front of the person
is the progress bar, the handoff and the thing they share, all at once.

- **Where:** `docs/ideas/<slug>.md` in the current repo, unless the person named a place.
  Outside a repo, use the current directory and say so.
- **Shape:** copy [`references/idea-doc.md`](references/idea-doc.md). Every section starts as
  `_pending_` and is replaced as its act closes.
- **Check:** `python3 ${CLAUDE_PLUGIN_ROOT}/skills/shape-an-idea/bin/idea-doc-check.py docs/ideas/<slug>.md`
  exits 0 only when every section is filled, the decision log holds at least one decision the
  person made, Workflow v0 records its N=1 run, and there are three next moves. Run it
  before you say the session is finished.

Write each decision into the doc the moment it is made, not at the end. If the session dies at
minute 20, the doc should still be worth reading.

---

## Act 1 — Shape (interview)

Goal: a problem statement the person would sign, and a short list of decisions that bound the
work.

Map the idea as a **decision tree**. Each decision opens the decisions that hang off it. Work
the tree in **rounds**:

1. **Ask the frontier, all at once.** The frontier is every decision whose prerequisites are
   already settled. Use the native question picker. It takes up to four questions per call, so
   batch them rather than asking one per turn.
2. **Recommend on every question.** Put your recommended answer first and mark it. A question
   without a recommendation pushes the thinking back onto the person.
3. **Never ask downstream of an open question.** If Q3 depends on how Q1 lands, Q3 waits for
   the next round.
4. **Recompute after every answer.** Settled decisions push the frontier outward.

Round one is almost always these four questions:

| Question | Why it comes first |
|---|---|
| Who is this for, specifically? | Every later answer depends on it |
| What does it replace or remove? | It names the status quo, which is the real competitor |
| What would "this worked" look like in a month? | It sets the bar the research has to clear |
| What is off the table? | Time, money, tools or people the idea cannot touch |

**Stop interviewing when** the problem statement and the bounding decisions fit on half a page
and the person agrees they read right. Show them the problem statement and ask:
**"Is this the idea?"** Don't go on to Act 2 until the answer is yes. Usually that takes two or
three rounds. If you are past five, the idea is really two ideas. Say so, and ask which one to
shape.

---

## Act 2 — Research (plan, then launch)

Goal: every claim the idea depends on, labelled either **known** (with a source) or
**unknown**, plus a plan that turns the unknowns that matter into known ones.

1. **List the assumptions.** Take each decision from Act 1 and write down what has to be true
   for it to hold. Most ideas rest on three to six of them.
2. **Rank by kill-power.** Which assumption, if false, ends the idea? Research that one first.
   An assumption that would only change the details goes to the bottom.
3. **Write one research question per assumption.** Each one gets a **method** (read the repo,
   search the web, query a connected tool, run a small spike), a **done-when** condition, and
   a **timebox**. See [`references/research-plan.md`](references/research-plan.md).
4. **Show the plan, then launch it.** Put the research plan in the doc, ask the person to cut or
   add questions in one picker round, then dispatch one sub-agent per question **in parallel**.
   Keep talking while they run. The workflow sketch in Act 3 can start on whatever does not
   depend on an open finding.
5. **Report findings as observations.** For each question: what was found, the source, and how
   confident you are. Leave out the because-clauses. What a finding *means* for the idea is
   the person's call, so ask them: keep going, change direction, or stop.

A spike counts as research. If the riskiest assumption is "the API can do X", fifteen minutes of
code against the API beats an hour of reading about it. Keep spikes in a scratch directory and
throw them away. They answer a question; they are not the product.

**Stop researching when** the kill-power assumptions are known, or when the person decides to
proceed without them. Record that decision in the log with its risk named.

---

## Act 3 — Workflow (rudimentary, proven at N=1)

Goal: the smallest repeatable version of the idea, written as steps, run once on one real
input.

1. **Write the steps as a table.** Columns: step, input, output, who or what does it (person,
   agent, script, existing tool). Five to nine rows. If you need more, the workflow is too big
   for a first version.
2. **Mark each step's rung.** Can it be a script, does it need an agent, or does it need the
   person? Pick the cheapest rung that will work. Most first versions are mostly manual, and
   that is fine.
3. **Run it once.** Pick one real input and walk it through every step. Do the agent and script
   steps yourself; ask the person for theirs. Note every step that broke or felt wrong.
4. **Write "next three moves".** Each one is concrete enough to start without another
   conversation, e.g. "run it on 10 inputs", "script step 4", "ask two users". These are
   proposals. The person picks.

**Do not build the full version.** The output of Act 3 is a workflow that ran once, not a
product. If the person wants to keep building, that is a new session. Hand it the idea doc as
the spec.

---

## Closing the session

The session is finished when all four of these are true:

- **Doc complete:** `idea-doc-check.py` (path above) exits 0.
- **Person confirmed:** they confirmed the problem statement in Act 1 and picked from the next
  moves in Act 3.
- **Scratch contained:** spikes live in a scratch directory, not mixed into the real codebase.
- **Pointer given:** the final message links the doc and lists the next moves the person chose.

Don't write a recommendation or verdict section for them. The doc records what was decided and
what was found. Any "should we do this?" paragraph is theirs to write.

---

## Pacing — it's a conversation, not a pipeline

- **Short turns.** One round of questions or one finding per message. Walls of text kill the
  back-and-forth that makes this work.
- **Interleave.** While sub-agents research, keep interviewing on independent branches or sketch
  workflow steps that do not depend on the findings.
- **Name detours.** If something will take more than about 15 minutes, such as a big spike or a
  long read, describe it as a trade and let the person decide whether to take it.
- **Let the person jump.** If they want to skip to the workflow, let them. Write down what was
  skipped as an open assumption so it stays visible.

---

## Gotchas

- **The first sentence is rarely the idea.** "A dashboard for X" usually means "I keep missing
  Y". Ask what triggered the idea. The trigger is often the real problem.
- **Agreeable answers are not decisions.** "Sure, sounds good" on your recommendation is weak
  evidence. On the decisions that bound the work, ask for the reason in their own words.
- **Research sprawl.** Every unknown looks researchable. Only kill-power assumptions get a
  sub-agent in the first pass. The rest go in the doc as open questions.
- **Silent tools lie.** A connector that returns nothing may be disconnected, not empty.
  Before reporting "nothing exists", make one call that must return something.
- **Spikes that become the product.** If spike code starts getting tests and a README, stop
  and ask whether the session has turned into a build.

---

Interview technique (design tree, frontier rounds, recommendation on every question) adapted
from [mattpocock/skills](https://github.com/mattpocock/skills) `grilling` (MIT).
