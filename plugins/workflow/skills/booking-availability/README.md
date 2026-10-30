# booking-availability

Diagnose a booking page that shows the wrong availability: no slots, slots on days you are
busy, or a link that 404s. It covers Cal.com and its Google Calendar connection.

## When to use it

- **Empty page**: "no booking slots" or "everything is blocked."
- **Wrong slots**: people can book over your real meetings.
- **Broken link**: the booking URL 404s.
- **Mixed symptoms**: some links are empty while others look fine.

Not for picking a meeting time for a group (use `find-meeting-time`) or creating one event at a
known time.

## How to use it

```
/workflow:booking-availability
```

Describe the symptom in plain words, e.g. *"no slots in September"* or *"people are booking
over my real meetings."*

The skill then works in this order:

1. Checks calendar credential health first. One expired or revoked credential often explains
   everything.
2. Counts slots for every event type over the same window. The pattern of zeros names the cause.
3. Maps each event type by scheduling type, schedule and hosts.
4. Checks schedule ownership, then schedule contents and the booking window.
5. Only then looks at calendar events, per day, longest first.

It explains why one dead calendar can blank collective event types while round-robin types look
fine, and why round-robin can still double-book that host.

## Example

A prospect says your link shows nothing for September. The skill finds one calendar returning
"Access token expired or revoked", sees that only collective event types are empty, and tells
you to disconnect and re-add that calendar in Cal.com settings. After you do, it re-counts
slots per weekday to confirm recovery.

## What you get

- **A diagnosis**: the cause, with slot counts per event type and per-day numbers as evidence.
- **Fix steps**: what to change and where.
- **Will not**: re-grant a Google login for you (that needs you), or delete events based on
  their shape alone. It prefers marking an event free over deleting it.

## Requirements

- **Cal.com API key**: supplied through a secret manager or environment variable. Keep it out
  of the command line and out of output.
- **curl** (and jq for reading responses).
- **Google Calendar connector** (optional): for reading events once credentials are healthy. It
  may see only some of your calendars.
- **Your own login**: for steps that are UI-only, such as disconnecting and re-adding a calendar.
