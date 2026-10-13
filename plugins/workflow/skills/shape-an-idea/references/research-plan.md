# Research plan — mechanics

How Act 2 turns assumptions into sub-agent work. The judgment lives in SKILL.md; this is the
how.

## One question per assumption

A good research question can be answered with a finding, not an essay.

| Weak | Strong |
|---|---|
| "Research the market for X" | "Name three tools that already do X, with pricing and the one thing each does badly" |
| "Can we integrate with Y?" | "Does Y's API expose Z on the plan we have? Show the endpoint and a real response" |
| "Will people want this?" | "In the last 90 days, how many times did the trigger problem appear in <source>?" |

## Pick the method

| Method | Use when | Typical timebox |
|---|---|---|
| Repo read | The answer is in code or docs you already have | 5–10 min |
| Web search | Prior art, pricing, public API capability | 10–15 min |
| Tool query | A connected app (CRM, analytics, calendar) holds the evidence | 5–10 min |
| Spike | "Can it actually do X?" (only running code proves it) | 15–30 min |
| Ask a human | Only a person outside the session knows | Record as an open question; don't block |

## Sub-agent brief template

Each sub-agent gets a self-contained brief. It has none of the conversation, so put
everything it needs in the brief:

```
Research question: <R#: the question>
Why it matters: tests assumption <A#: text>. If false, <consequence>.
Method: <method>. Timebox: <minutes>.
Done when: <condition>.
Return: (1) the finding as one or two observation sentences, no interpretation;
(2) sources: links, file paths or the exact query run; (3) confidence high/med/low and
why; (4) anything surprising that the question did not ask about, in one line.
Do not write files outside <scratch dir>. Do not make recommendations.
```

Launch every independent brief in **one message** so they run in parallel. A spike that needs
a sandbox should get an isolated worktree or scratch directory.

## Reporting back

Write each finding into the idea doc under its question, then tell the person in chat in one
line per finding. Update the assumption's status. When a finding contradicts a decision,
re-open that decision as a question in the next round. Don't quietly patch around it.

## When the research says stop

If a kill-power assumption comes back false, say so plainly, first, with the source. Offer
the options as a picker: pivot (which decision to re-open), shrink (what survives), or stop.
The skill's job is to get the evidence in front of the person, not to rescue the idea.
