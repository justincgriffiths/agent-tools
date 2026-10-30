# find-meeting-time

Find when a group can actually meet. It reads real Google Calendar free/busy, recommends one
slot with the tradeoff named, and books it once you approve.

## When to use it

- **Group scheduling**: three or more people and you need one invite.
- **"No time works"**: you need to know who or what is blocking, not just that it fails.
- **Thread-driven booking**: an email thread says "let's schedule" and you want it handled.

Not for a 1:1 you can eyeball, creating an event at a time already chosen, or people whose
calendars you cannot read.

## How to use it

```
/workflow:find-meeting-time
```

Say who you want to meet in plain words, e.g. *"find a time for me, Dana and Lee next week."*
Anything you leave out is asked, not required.

The skill then:

1. Asks for gaps (duration, window, which person if a name is ambiguous) in one picker call.
2. Resolves names to real calendar addresses instead of guessing from a domain pattern.
3. Queries the group, then each person separately, to find who is blocking.
4. Tries at least two durations, because an hour may not exist when 30 minutes does.
5. Reads each person's timezone from events they organized, and asks you when it would change
   the answer.
6. Recommends one slot and one backup, with what is blocked and by whom.
7. Books only after you say so.

## Example

```
Book it Tue, 1:00-1:30pm ET.
Backup: Fri, 9:00-9:30am ET.

A full hour does not exist next week; 30 minutes exists twice.
- Thursday is blocked by one person's recurring all-day block.

Nothing sent. Say the word and I'll create it.
```

## What you get

- **A recommendation**: one slot, one backup, and the constraint that binds.
- **A calendar invite**: created only after you approve, with a title and video link you choose.
- **Will not**: send an invite unprompted, call a conflict movable (free/busy hides titles), or
  see calendars on accounts the connection cannot reach.

## Requirements

- **Google Calendar connector**: an MCP connector for Google Calendar. Its tools are loaded on
  demand.
- **Read access**: to every attendee's calendar. External attendees usually return nothing, and
  the skill then proposes two or three options instead.
- No CLIs, scripts or API keys.
