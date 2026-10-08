---
name: find-meeting-time
description: Find when a group can actually meet, using Google Calendar MCP free/busy — resolve who the people are, read their real availability, recommend one slot with the tradeoff named out loud, and book it once approved. Use for "find a time for X", "when can we all meet", "book the partner meeting", "what's a good slot next week for A/B/C/D", or any ask whose end state is a calendar invite for 3+ people. Owns the judgment free/busy cannot express — whose working hours actually apply, who the single blocker is, and whether the duration was ever the real constraint. SKIP for a 1:1 you can eyeball, for creating an event at a time already chosen (that is just create_event), and for anyone whose calendar you cannot read.
argument-hint: "who to meet — say it plainly; anything you leave out gets asked, not required"
intake:
  required: [people]
  optional: [duration, window, timezone, title, context]
created: 2026-08-14
verified: 2026-08-17
source: extracted from the author's working sessions, 2026 — a five-person meeting, week of 2026-08-17. Two viable slots existed all week; a wrong timezone inference nearly buried both under a caveat that did not apply.
summary: "Find when a group can actually meet from Google Calendar free/busy, recommend one slot with the tradeoff named, and book it once approved"
group: "Capture & meta"
---

> **Receipt (2026-08-17):** the recommended slot was booked, Tue 2026-08-18 13:00 ET
>
> (This detail used to be appended to `verified:`, which is an ISO date — the fact
> was worth keeping, the place was wrong.)

# find-meeting-time

Scheduling looks like a lookup and is actually a judgment call. The API answers *when is
nobody's calendar occupied*. Nobody asked that. They asked **when should this meeting happen**,
which depends on working hours, who can move what, and whether the duration was ever real.

**The failure this prevents:** reporting "no times available" when you queried the wrong
duration, or calling a slot bad because you inferred a constraint from someone's timezone that
the team had already solved for.

Tool names, parameter shapes, and the free/busy semantics live in
[`references/mechanics.md`](references/mechanics.md). **Read it before the first call** — the
calendar tools are not loaded by default, and the search API silently truncates.

---

## The one rule

> **Free is not available.**

Google free/busy has no concept of working hours, sleep, or lunch. It will report 2:00am local
as free, every day, for everyone. An unbooked hour is not an offer.

Everything below closes the gap between *unbooked* and *actually a good time*.

---

## Gathering the inputs

Three things determine the search: **who**, **the window**, and **the duration**. Take whatever
the request already states, and ask for the rest with the **native question picker** — never by
requiring flags or a particular phrasing. The person asking should be able to say "find a time
for me and Dana next week" and be done.

**Batch every gap into one picker call.** It takes up to four questions at once. Three separate
prompts for who/when/how-long is three interruptions for one answer.

Ask for:

- **Duration**, when nothing implies it — offer 30 / 45 / 60.
- **Which person**, when a first name resolves to more than one address. Put the candidate
  addresses in the options. This is the one gap you must never paper over with a guess.
- **The window**, only when phrasing like "next week" is genuinely absent.

Don't ask for:

- Anything already stated. "Me and Dana next week" has two of the three.
- Anything you can resolve yourself — the date arithmetic, the organizer's own timezone
  (`list_calendars` returns it), names that resolve unambiguously.
- **Duration, when the meeting has a precedent.** If a prior instance of the same meeting
  exists, its length is the answer. Look before you ask.

A question you could have answered from the calendar is a worse interruption than a flag.

### When the meeting comes from an email thread

Read the thread before you touch the calendar, and **read it to the end**. Most of the inputs
are already in it — the date someone proposed, the window the other side offered, who belongs
on the invite. So is the one thing free/busy can never tell you: **whether the meeting should
be scheduled at all.**

**Verified 2026-08-17.** A follow-up that arrived as a pure scheduling task ("book it for next
week") had, as the *most recent* message, the client saying that a written agreement had to
be in place before scheduling another meeting. Both internal calendars were wide open
across the proposed window. Availability was never the constraint. Booking on the strength of
the earlier "let's lock it in" — three messages up — would have pushed an invite at a prospect
who had just asked for the opposite.

**The last message wins.** An agreement earlier in a thread can be withdrawn by the one below
it, and the withdrawal is invisible from the calendar. When the thread and the request
disagree, surface it and let the human resolve it — the blocker may already be handled
somewhere you can't see, like a phone call.

---

## Procedure

### 1. Resolve the people before you resolve the time

You are given first names. You need calendar IDs. **Do not construct addresses from a domain
pattern** — the pattern holds until it doesn't (shared aliases, contractors on another domain,
two people with one first name).

**Verified 2026-08-14:** `list_events` with `fullText: "<FirstName>"` matches against the
attendee list, so one call against a recurring all-hands returns the whole roster with real
addresses and display names. Four names resolved in a single call this way.

Stop if a name is ambiguous. Booking the wrong Sam is worse than asking.

### 2. Establish the window in the user's own terms

"Next week" is Monday–Friday of the following week. Compute it — check the real date and
day-of-week rather than trusting the model's sense of today.

### 3. Query the group, then query every individual separately

This is the step people skip, and it is where the value is.

- The **group** call tells you *what* is free.
- The **per-person** calls tell you *who is blocking everything else*.

Only the second produces a recommendation worth reading. "Nothing works" is a dead end.
"Nothing works, and one person's single conflict stands between you and a full hour on Friday
morning" is an action. You cannot write the second sentence from the group call alone.

Run the per-person calls in parallel; they're independent.

### 4. Treat duration as a variable, not a given

**Verified 2026-08-14:** the same five people over the same week returned **zero** 60-minute
slots and **two** 30-minute slots. Asking once, at 60, reports "no availability" — wrong, in a
tone that sounds authoritative.

Probe at least two durations. Report the shape: *an hour doesn't exist; thirty minutes exists
twice.*

### 5. Work out whose hours actually apply — and ask when it changes the answer

Read each attendee's timezone off the `timeZone` field of events **they organized**, never off
their email domain or your assumption about where they live.

**Verified 2026-08-14:** two attendees' events were stamped `Europe/Madrid` and
`Europe/Lisbon` — invisible from their `@company.com` addresses.

**Then stop, because this is the trap.** Location is not working hours. A distributed team
often standardizes on one timezone's business day and the people abroad have opted in. In the
motivating session the correct read was the user's: the team works US east-coast hours, so up to
early afternoon (theirs) is fine. Inferring a 7:00pm-Madrid imposition from a Madrid
stamp was about to bury the only two workable slots under a caveat that did not apply.

The rule: **when a timezone inference would change your recommendation, ask instead of
inferring.** One line, cheap. Guessing costs a good slot; asking costs a sentence.

### 6. Name the tradeoff, then recommend one

Lead with a single slot and a single backup, then the constraints that are load-bearing: what
doesn't exist at all, and what's blocked by one movable thing. Do not present a ranked list of
six — that hands the judgment back to the person who asked you to make it.

### 7. Present, then book on an explicit go-ahead

Finding a time is not booking it. An invite is outward-facing, lands in several other people's
inboxes, and is awkward to retract. Offer; don't send.

On approval, settle whatever is still unknown in **one** picker call — typically the title and
whether it carries a video link, and which (a Meet link is one parameter; a Zoom link goes in
`location`). Don't re-ask the slot — they just approved it. The parameter shape, the
deprecated-field trap, and the notification switch are in
[`references/mechanics.md`](references/mechanics.md#booking-it).

Booking is the one destructive step here. Everything before it is read-only and safe to retry.

---

## Gotchas

**`suggest_time` returns a bare `{}` when nothing fits.** *Verified 2026-08-14, re-confirmed
2026-08-17.* An empty object — not an error, not an empty array, no message. Indistinguishable
at a glance from a broken call. Before reporting "no availability," re-run at a shorter
duration or with a subset of attendees to prove the tool is answering at all. An unverified
`{}` reported as fact is the highest-cost mistake available here.

**The slot list is capped at 5 by default.** *Verified 2026-08-17 from the schema.*
`preferences.pageSize` defaults to `5`, so a week-long query silently returns the first five
openings and looks complete. Set it explicitly (25 is comfortable) or you will recommend from
a truncated picture without knowing it.

**`accepted` and `tentative` block; `declined` does not.** *Verified 2026-08-17* by three-way
comparison on a single event, each attendee's busy block matching the event bounds exactly:

| Response | Free/busy across the event |
|---|---|
| `accepted` | **Busy** |
| `tentative` | **Busy** — indistinguishable from accepted |
| `declined` | **Free**, continuous straight through |

Free/busy reflects *intent to attend*, not invitations — and a maybe counts as a yes. Two
consequences worth carrying: a slot you rule out may actually be viable, because the thing
blocking it is somebody's tentative "probably not" that free/busy renders as a hard no; and a
slot that looks open because someone declined closes again silently if they un-decline.

**The connection may only see one of the user's calendars — and `suggest_time` inherits that
blindness.** *Verified 2026-08-17, and the dangerous half found 2026-08-21.*
`list_calendars` returns the calendars of the **connected account only**. A second work
identity on another Google account — a client-facing address, a separate business domain — is
invisible: its meetings never surface as precedent (so "look before you ask" on duration comes
back empty and you ask anyway), and you cannot create an event on it. Call `list_calendars`
early. If the identity the thread is conducted under isn't in the list, say so and let the
human send the invite rather than firing one from an address the recipient doesn't recognise.

**The worse half is that your availability answers are wrong.** This gotcha used to stop at
"you cannot create events there", which reads like an inconvenience. It is not.
`suggest_time` computes free/busy from the **connected account's** calendars, so a slot it
reports as free for everyone can be occupied on another calendar the same person owns — and
if that calendar feeds a booking tool, it is occupied in a way that matters.

*Verified 2026-08-21:* `suggest_time` reported a Wednesday morning free for three attendees. A
seven-and-a-half-hour opaque block sat on the requester's second work calendar. Two meetings
were moved into it and had to be moved again, costing three people a second notification. It
produced a second wrong answer the same day on a different Wednesday.

So: **probe every calendar by id, not just the ones `list_calendars` returns**, and read
`accessRole` on each — `owner` is read-write, `freeBusyReader` gives times without titles,
and not-found means invisible **while still constraining the booking tool**. Then confirm the
destination with a per-day slot census (count bookable slots per day in the booking tool),
which is what caught this. A day whose first bookable slot is hours later than its neighbours' is a block
you have not found, and its edge gives you the block's end time to the minute.

**Whole days can be blocked by policy, not by meetings.** *Verified 2026-08-14.* One attendee
held a recurring all-day "No Calls Day" that renders in free/busy as an ordinary busy block.
Nothing will ever schedule there and it is not a conflict you can ask them to move. Scan for
all-day and recurring blocks before proposing anything on that day.

**Opaque "Busy —" mirror events are real.** *Verified 2026-08-14.* Cross-calendar busy mirrors
carry no detail by design; the real event lives on another calendar. Treat them as hard blocks.
Their emptiness is not evidence that they're soft.

**A slot bounded on both sides is exactly its length.** When the group's only opening is 30
minutes because two people free up at 1:00 and are booked again at 1:30, say so — otherwise
someone will try to run 45 minutes into it.

**Free/busy hides *why*.** You get busy blocks, never titles. You cannot tell a movable
internal sync from a client call. Never assert that someone's conflict is movable — say it
*may* be, and let the human judge.

---

## Output shape

Lead with the booking, not the methodology:

```
Book it <Day, Date, time range + tz>.        ← one recommendation
Backup: <same>.                               ← one alternative

<Why these are the only ones — the constraint that binds.>

- <What doesn't exist at all, e.g. "a full hour doesn't exist next week">
- <What's blocked by one movable thing, and whose>
- <Any day that's dead for a structural reason>

Nothing sent — say the word and I'll create it.
```

Roughly six lines. Longer means you're narrating the search instead of answering it.

---

## When not to use this

- **A 1:1.** Open the calendar and look.
- **The time is already chosen.** That's `create_event`, not this.
- **Calendars you can't read.** External attendees usually return nothing useful; the skill
  degrades to proposing 2–3 options and asking. Say that's what you're doing rather than
  presenting guesses as availability.
