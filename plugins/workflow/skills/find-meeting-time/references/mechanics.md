# Mechanics — Google Calendar MCP

Tool names, parameter shapes, and semantics. The judgment lives in `../SKILL.md`; this file is
the part you'd otherwise rediscover by trial and error.

All claims marked **Verified** were exercised against a live calendar on the stated date.

---

## 0. Load the tools first

**Verified 2026-08-14.** The Google Calendar MCP tools are **deferred** — they are not in the
default tool set, and calling one by name without loading it fails with
`InputValidationError`. The server may also still be connecting at session start, in which case
a keyword search waits for it.

Load them before the first call:

```
ToolSearch("select:mcp__claude_ai_Google_Calendar__suggest_time,
            mcp__claude_ai_Google_Calendar__list_events,
            mcp__claude_ai_Google_Calendar__list_calendars,
            mcp__claude_ai_Google_Calendar__create_event")
```

Never report "no calendar access" without running a `ToolSearch` first — absence from the
default tool list is not absence of the capability.

## 1. Tool inventory

| Tool | Use it for |
|---|---|
| `list_calendars` | Resolve the user's own calendar ID + **their primary timezone** (returned as `timeZone`) |
| `list_events` | Resolve people from attendee blocks; read the real schedule; spot all-day and policy blocks |
| `search_events` | Semantic search, **primary calendar only**. Weak for roster lookup — prefer `list_events` + `fullText` |
| `suggest_time` | Cross-calendar free/busy intersection. The workhorse |
| `create_event` | Book it, once approved |
| `get_event` | Re-read one event by ID after booking |

---

## 2. `suggest_time` — the contract

```jsonc
{
  "attendeeEmails": ["a@x.com", "b@x.com"],   // required
  "startTime": "2026-08-17T08:00:00-04:00",    // required, ISO 8601
  "endTime":   "2026-08-21T19:00:00-04:00",    // required
  "durationMinutes": 30,                        // default 30
  "timeZone": "America/New_York",              // IANA; governs the preference hours
  "preferences": {
    "startHour": "08:00",                       // "HH:mm", 24h
    "endHour":   "19:00",
    "excludeWeekends": true,
    "pageSize": 25                              // DEFAULT 5 — always set this
  }
}
```

**Returns `{}` when nothing fits.** *Verified 2026-08-14, re-confirmed 2026-08-17.* A bare
empty object. No error, no empty array, no message. It is visually identical to a failed call.
Always disprove a `{}` by re-running at a shorter duration or with fewer attendees before
reporting "no availability."

**`pageSize` defaults to 5.** *Verified 2026-08-17 (schema).* Omit it and a five-day query
returns five openings and looks exhaustive. This is the silent-truncation trap in this API.

**Returned slots are merged maximal free blocks, not fixed-length options.** A returned slot
carries its own `durationMinutes`, often much larger than you asked for (a 60-minute query can
return a 405-minute block). `durationMinutes` in the request is a *minimum*, not a slot size.

**It has no concept of working hours.** `preferences.startHour`/`endHour` are the only thing
keeping it from offering 3:00am. They are applied in `timeZone` — one timezone for the whole
query, so for a cross-timezone group you're choosing whose day the window describes.

---

## 3. Resolving people with `list_events`

**Verified 2026-08-14.** `fullText` matches attendees as well as title/description/location, so
searching a first name against a group event returns the full roster:

```jsonc
{ "fullText": "Dana", "orderBy": "startTimeDesc", "pageSize": 5 }
```

Each event carries an `attendees[]` of `{email, displayName, responseStatus, organizer}`. One
call against a recurring all-hands resolved four first names to addresses.

`orderBy: "startTimeDesc"` without a time bound can surface far-future recurring instances
(years out). Harmless for roster lookup — you only want the attendee block — but don't read the
dates as "upcoming."

### Reading someone's timezone

There is no "get this person's timezone" call. Infer it from the `timeZone` field on events
**they organized** — Google stamps the organizer's zone. *Verified 2026-08-14:* attendees on
`@company.com` addresses turned out to be `Europe/Madrid` and `Europe/Lisbon`.

`list_calendars` gives you the *user's own* timezone directly and reliably. Everyone else is
inference — see the SKILL's step 5 on when to stop inferring and ask.

---

## 4. What free/busy does and doesn't expose

| You get | You don't get |
|---|---|
| Busy intervals for any attendee | Event titles, attendees, or importance |
| Whether a block exists | Whether it's movable |
| All-day and recurring blocks, as ordinary busy | Any flag distinguishing policy from a meeting |

**`responseStatus` drives free/busy.** *Verified 2026-08-17*, three-way comparison on a single
event (AI Skills Workshop, Tue 2026-08-18, 08:30–09:30 ET). Each busy block matched the event
bounds exactly, so nothing else explains it:

| `responseStatus` | Free/busy across 08:30–09:30 |
|---|---|
| `accepted` | **Busy** — free 08:00–08:30, resumes 09:30 |
| `tentative` | **Busy** — identical to `accepted` |
| `declined` | **Free** — one continuous 08:00–10:00 block |

Replicated for `accepted` vs `declined` on a second, independent event (Fri 2026-08-21,
09:00–09:30 ET).

So free/busy tracks *intent to attend*, not invitations, and **a maybe is stored as a yes**.
Don't diff it against an event list and conclude the API is lying. Two directions of risk: a
slot open because someone declined closes silently if they un-decline; and a slot you discarded
may be fine, because the only thing blocking it was a `tentative` nobody intends to honour.
Free/busy cannot distinguish that — if a week looks impossibly tight, a human asking "is that
Tuesday thing real?" beats another query.

**Opaque busy mirrors.** Cross-calendar sync tools write detail-free placeholders (e.g.
`Busy — work` / `Busy — personal`). They are real blocks whose detail lives on another calendar. Their emptiness is
not softness.

---

## 5. Booking it

Only after an explicit go-ahead. Confirm duration, title, and video-link need first.

```jsonc
{
  "summary": "Partner update",
  "startTime": "2026-08-18T13:00:00-04:00",
  "endTime":   "2026-08-18T13:30:00-04:00",
  "timeZone":  "America/New_York",
  "attendees": [                                 // NOT attendeeEmails
    {"email": "dana@acme.com"},
    {"email": "sam@acme.com"}
  ],
  "addGoogleMeetUrl": true,
  "notificationLevel": "ALL"
}
```

- **`attendees` — `attendeeEmails` is deprecated.** Use the object array; it's the only form
  that carries `optionalAttendee` and `displayName`.
- **`notificationLevel` defaults to `ALL`** — i.e. creating the event emails everyone
  immediately. That default is usually right for a meeting people are expecting, and wrong for
  anything you're staging. `NONE` writes silently; `EXTERNAL_ONLY` spares the internal team.
- **`timeZone` overrides the offsets in `startTime`/`endTime`.** Don't set it to one zone and
  write offsets from another.
- The organizer is added automatically when creating on their own primary calendar with at
  least one other attendee.
- `addGoogleMeetUrl: true` mints a Meet link. If the house standard is Zoom, don't — attach the
  Zoom URL as `location` instead.

**Verify by re-reading, not by assuming.** `get_event` with the returned ID, or re-run
`suggest_time` over that window — a correctly booked slot disappears from the group's
availability. *Verified 2026-08-17:* after the partner meeting was created for Tue 13:00–13:30,
the Tuesday group query went from one slot to `{}`.

---

## 6. Worked example — the motivating session

Five attendees, one week (2026-08-17 → 08-21), partner meeting.

1. `ToolSearch` to load the calendar tools.
2. `list_calendars` → organizer is `America/New_York`.
3. `list_events` `fullText` per first name → four addresses in one call.
4. `suggest_time` all five, 60 min → **`{}`**.
5. Same query at 30 min → **two slots**, Mon and Tue, both 13:00–13:30 ET. The `{}` was real,
   and duration was the binding constraint.
6. `suggest_time` per person, in parallel → two partners are the pair that bound both slots
   to exactly 30 minutes; a 4-of-5 hour existed Friday morning blocked only by one of them.
7. Timezone read: two attendees in Iberia. **Asked rather than inferred** — the team works ET
   by choice, so 13:00 was fine and the caveat was dropped.
8. Presented one slot + one backup. Did not send.
9. The user booked Tuesday themselves. Post-hoc `suggest_time` on Tuesday → `{}`. Loop closed.
