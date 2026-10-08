---
name: booking-availability
description: Diagnose and fix a booking page that shows the wrong availability — no slots at all, slots on days you are busy, or a link that 404s. Covers Cal.com + its Google Calendar connection end to end, in the order that finds the cause fastest. Use for "no booking slots", "cal.com shows everything blocked", "my booking link is broken", "prospects can't book", "slots are showing when I'm busy", "why is my calendar link empty". Owns the CREDENTIAL-FIRST diagnostic order and the collective-vs-roundRobin asymmetry that makes one dead calendar produce two opposite symptoms. SKIP for picking a meeting time for a group (that is find-meeting-time) and for creating a single event at a known time (that is just create_event).
argument-hint: "the symptom in plain words — no slots in September, or people booking over my real meetings"
intake:
  required: [symptom]
  optional: [window, event-type, who, platform]
created: 2026-08-21
verified: 2026-08-21
source: extracted from the author's working sessions, 2026 — a Cal.com incident, 2026-08-20/21. Two hours went into calendar events and schedule config before checking credential health, which was the answer and is one API call.
summary: "Diagnose a booking page serving the wrong availability — credential health first, then the collective-vs-roundRobin split that makes one dead calendar look like two bugs"
group: "Capture & meta"
---

# booking-availability

A booking page showing no slots looks like a schedule problem and usually is not. The
schedule is the thing you can see, so it is the thing you check — and it will look perfectly
healthy while the real cause sits one field away in a different endpoint.

**The failure this prevents:** spending the session auditing working hours, date overrides,
booking windows, and calendar events, when a single dead OAuth credential explains everything.

API endpoints, exact version headers, which routes 404, and the secret-safe curl pattern live
in [`references/calcom-api.md`](references/calcom-api.md). **Read it before the first call.**

---

## The one rule

> **Check credential health before you check anything else.**

`GET /v2/calendars` returns an `error.message` per connected calendar. If any says
`Access token expired or revoked`, that is your answer — stop diagnosing and go fix it. A
booking tool that cannot read a calendar does not guess; it takes the safe branch, and the safe
branch is usually "unavailable."

Everything below is for after you have confirmed the credentials are healthy.

---

## Why one dead calendar produces two opposite symptoms

This is the part that reads as two unrelated bugs and is one cause. Cal.com event types differ
in how many hosts must be free:

| Scheduling type | Needs | A dead credential on one host means |
|---|---|---|
| `collective` | **every** host provably free | **0 slots.** Fails closed. |
| `roundRobin` | **any** host free | **Looks fine.** A healthy co-host masks the dead one. |
| personal (no team) | just the owner | **0 slots** if the owner's calendar is dead. |

So the same broken credential simultaneously blanks some links and leaves others apparently
working. Do not treat those as separate investigations, and do not conclude "personal is broken,
team is fine" — the split is by scheduling type, not by ownership.

**The round-robin case is not harmless.** A host whose calendar cannot be read is treated as
free, so round-robin can still assign that person a booking on top of a real commitment. It
fails quietly instead of loudly, which is worse.

---

## Diagnostic order

Do these in order. Each step either ends the investigation or narrows it.

1. **Credential health** — `GET /v2/calendars`. Read `error.message` on every entry. Also check
   `destinationCalendar`: empty-string `integration` and `externalId` are a symptom of the same
   broken credential, not a separate misconfiguration.

2. **Slot counts per event type, side by side** — `GET /v2/slots?eventTypeId=…` for *every*
   event type over the same window. The **pattern of zeros** is the diagnosis. All zero → a
   global cause (credential, or the one schedule everything inherits). Some zero → read the
   table above.

3. **Map each event type** — `GET /v2/event-types` for the inventory, then per-type detail for
   `schedulingType`, `scheduleId`, and `hosts[]`. Group the zeros and the non-zeros by
   `scheduleId` and by `schedulingType`. The grouping names the mechanism.

4. **Schedule ownership** — `GET /v2/schedules/{id}`. A **403 means the schedule is not yours**;
   it belongs to a co-host. That is how you discover a "working" event type is riding someone
   else's availability rather than your own. Use it deliberately as an ownership probe.

5. **Only now, the schedule contents and booking window.** `periodType: UNLIMITED` plus
   sane `availability` rules out limits. Date overrides in the *past* are irrelevant — check
   the dates before blaming them.

6. **Only now, calendar events.** See the calendar-events section below.

---

## Traps

**Adding a calendar does not repair a broken one.** Connecting more accounts to the same user
leaves the errored credential in place, and availability keeps failing closed. The fix is
**disconnect the broken connection, then re-add it** — Settings → Calendars → the entry showing
an error → Disconnect → Add again. *Verified 2026-08-21: new accounts were added to the same
user and `/v2/calendars` still returned exactly one connection, still revoked.*

**A healthy-looking schedule plus zero slots is not a schedule bug.** Mon–Fri 09:00–17:00,
`isDefault: true`, correct timezone, no limits — and still zero. That combination is the
signature of a read failure upstream, not a config error.

**`scheduleId: null` is not "no schedule."** It means inherit the owner's `defaultScheduleId`.
Every event type with `null` shares one fate, which is why they all go dark together.

**A 404 on the booking URL is a wrong slug, not broken availability.** Enumerate the real slugs
before concluding anything about slots. Docs and memory drift; the API is the truth.

**An event type with zero hosts assigned returns zero slots forever**, independent of any
calendar. Check `hosts[]` is non-empty before blaming infrastructure.

**Suspect the org's OAuth policy on repeat revocations.** Google Workspace *App access control*
can block or revoke a third-party app's grant, so reconnecting works and then breaks again on a
cycle. If a credential has died more than once, the durable fix is a Workspace admin trusting
the app's client ID, not another reconnect. *Unverified — plausible cause in the 2026-08 incident,
never confirmed with an admin.*

---

## When calendar events really are the cause

Reach here only after credentials are healthy. Then the question is whether something is
occupying time that should be free.

- **`transparency: transparent` means free.** All-day events, working-location entries, and
  "Tank top thursday" style markers are transparent and can never block a slot. Filter them out
  before counting.
- **Compute per-day free time inside the booking window**, rather than eyeballing a list. One
  long event hides behind dozens of short ones.
- **Sort by duration, descending.** One multi-day block is the usual culprit and sorts straight
  to the top.
- **A long block is not evidence of a bug.** *Corrected 2026-08-21 — this skill previously
  claimed a block spanning days at odd boundaries (09:45 → 10:00 a fortnight later) was a "merge
  artifact." That was wrong.* The 336h block in the founding incident was a **real event**: a
  colleague's two-week absence. Shape tells you nothing about legitimacy. Get the
  title and the origin calendar before forming a theory.
- **The real bug class is whose-time-is-this, not is-this-real.** A colleague's absence, a
  company holiday, an FYI hold — all legitimate, none of which should consume *your* bookable
  time. Ask **"is this event occupying time I actually cannot be booked in?"** If it is
  informational about someone else, the fix is to mark it free/`transparent` or move it off the
  calendars that feed booking availability. **Deleting it destroys information you wanted.**
- **Finding real meetings inside a long block does not make the block fake.** It only proves
  *you* were not away. In the founding incident 29 of the user's own meetings sat inside the
  fortnight — which was consistent with the block being genuine and belonging to someone else.
  That heuristic reached the right action for the wrong reason; do not lean on it.
- **So: never delete on shape alone, and prefer free/busy over deletion.** Read the title. If
  you cannot read the title (see `accessRole` below), you are not yet entitled to delete
  anything — escalate to whoever can.
- **Save a restore manifest before bulk deletion**, especially if whatever generated the events
  can no longer run — then the delete is genuinely irreversible.

Google Calendar MCP mechanics (token limits, retry behavior, transient errors) are in
[`references/calcom-api.md`](references/calcom-api.md#google-calendar-mcp).

---

## Purging a mirror from one calendar is not enough

**Verified 2026-08-21 — the sharpest trap in this whole area.** A mirror writes to *every*
calendar it targets. Cleaning the one calendar you can read, then connecting the others to the
booking tool, **re-exposes the identical phantom blocks** — same dates, same symptom, and it
reads as a regression of a fix that actually worked.

In the incident: 126 mirrors were purged from the user's primary calendar (`sam@acme.com`) and availability recovered.
Reconnecting the other four calendars blanked the *exact same 11 weekdays* again, because copies
of a ~340h event (Aug 26 → Sep 9 — a colleague's real absence) and a 49.5h one (Sep 18 → Sep 20)
sat on **three** other calendars untouched.

**Clean every calendar the mirror targeted before you connect them, or expect the second wave.**

### Locating bad blocks on a calendar you cannot read

You often cannot reach every calendar — the Google Calendar MCP is scoped to whatever accounts
were granted, typically one. But once a calendar is connected to Cal.com, **Cal.com can read it
for you**: `GET /v2/calendars/busy-times`, one calendar at a time, isolates which calendar owns
a block.

```bash
# curl -g is REQUIRED — the bracket syntax is otherwise parsed as a glob range
URL="https://api.cal.com/v2/calendars/busy-times?loggedInUsersTz=America%2FNew_York\
&dateFrom=2026-08-26&dateTo=2026-09-09\
&calendarsToLoad[0][credentialId]=${CRED}&calendarsToLoad[0][externalId]=${ENC_EMAIL}"
curl -sS -g --config - "$URL"
```

Query each selected calendar separately and sort spans by duration. The calendar whose
`total_busy` is an order of magnitude larger than the others is the one holding the garbage.
This turns "some other calendar is blocking me" into "delete these two events from these three
calendars" — which is a request a human can act on in a minute.

Get `credentialId` + `externalId` from `GET /v2/calendars`
(`.connectedCalendars[].calendars[] | select(.isSelected==true)`).

### Two ways out when you cannot edit the offending calendar

1. **Borrow access (preferred).** Pass the foreign calendar id straight to the calendar tool —
   you can read anything your authenticated user has an ACL on. If `accessRole` comes back
   `freeBusyReader`, ask the owner to raise it to *Make changes to events*, then delete the
   phantoms and keep conflict checking.
2. **Deselect it (emergency).** `DELETE /v2/selected-calendars` unblocks immediately with no
   human in the loop — but it also stops that calendar's *real* events counting. Reversible;
   state the exposure when you use it.

### Confirm recovery per-day, not in aggregate

A healthy total slot count hides a contiguous dead zone. Print **slots per weekday** across the
window; a run of consecutive zeros is a multi-day block, and its edges give you the block's
start and end without reading a single event.

---

## Do not rebuild cross-calendar busy mirroring

Copying busy blocks between calendars so one calendar "knows" about another is an anti-pattern.
It was tried and it was killed 2026-08-20. Its real defects: it copied one meeting up to three
times onto the same calendar, its own cleanup script filtered on a different property key than
the writer set (so cleanup was a silent no-op), and it re-published colleagues' absences onto
calendars that feed booking availability, marked BUSY.

Mirroring re-derives state that the booking tool already computes correctly. **Connect every
calendar to the booking tool directly and let it do conflict checking.** If someone asks for a
mirror, the answer is a second calendar connection.

Corollary: a cleanup script that filters on a different property key than the writer sets is a
silent no-op. If a cleanup "ran fine" and changed nothing, compare the exact key both sides use.

---

## Reporting

The user asked why nobody can book them. Lead with whether that is fixed.

- If the remedy is an OAuth re-grant, **you cannot do it** — it needs their login. Say so in one
  line, give the exact URL, and do not bury it under what you did manage to clean up.
- Name the two symptoms separately when both exist. "Some links are empty" and "some links are
  overbooking you" have one cause but different consequences, and the second is the one they do
  not know about.
- Verify recovery with numbers, not assertion: per-day free hours before and after, slot counts
  per event type.

---

## Provenance

Verified 2026-08-21 against a live incident: the user's "every slot blocked across August and
September" report traced to a revoked Google OAuth credential, found by `GET /v2/calendars` in
one call after roughly two hours had gone into schedules, date overrides and calendar events
that were never broken. The second wave arrived when reconnecting the other calendars
re-exposed the same phantom busy blocks from calendars that had never been purged — which is
why "recovery" gets confirmed per-day, not in aggregate.
