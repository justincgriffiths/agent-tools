# Cal.com API + Google Calendar MCP mechanics

Everything marked **Verified 2026-08-21** was executed against a live Cal.com account during
the 2026-08-20/21 incident.

---

## Credentials

**Verified 2026-08-21.** The API key lives in a secret manager — e.g. a 1Password secret reference
`<your-cal-api-key-secret-ref>` (put your own Cal.com API key reference here).

If the Cal.com login is Google SSO, there is no Cal.com password to hand an agent. So UI work
needs the user; API work does not.

### Keeping the key out of argv

`curl -H "Authorization: Bearer $KEY"` puts the secret in the process table. Feed the header
through stdin instead — `printf` is a shell builtin, so nothing is exec'd with the value:

```bash
q() {  # q <outname> <api-version> <url>
  printf 'header = "Authorization: Bearer %s"\nheader = "cal-api-version: %s"\n' "$CAL_KEY" "$2" \
    | curl -sS --max-time 40 --config - "$3" -o "$1.json" -w "  $1 http=%{http_code}\n"
}
```

Launch under `op run` so the value never reaches stdout:

```bash
op run --no-masking \
  --env-file=<(echo 'CAL_KEY=<your-cal-api-key-secret-ref>') -- ./probe.sh
```

---

## Endpoints that work

**Verified 2026-08-21.** The `cal-api-version` header is **per-endpoint** — a wrong one returns
a confusing error rather than a version complaint. These pairings are confirmed:

| Endpoint | `cal-api-version` | Returns / notes |
|---|---|---|
| `GET /v2/me` | `2024-06-11` | `id`, `username`, `email`, `timeZone`, **`defaultScheduleId`**, `organizationId` |
| `GET /v2/calendars` | `2024-06-11` | `connectedCalendars[]` each with `credentialId` + **`error.message`**; plus `destinationCalendar` |
| `GET /v2/schedules` | `2024-06-11` | only schedules **you own** — a schedule used by your event types can be absent |
| `GET /v2/schedules/{id}` | `2024-06-11` | `availability[]`, `overrides[]`, `isDefault`. **403 = not yours** (ownership probe) |
| `GET /v2/slots?eventTypeId={id}&start=&end=&timeZone=` | `2024-09-04` | `{"data":{}}` when there are none. `start`/`end` accept `YYYY-MM-DD` |
| `GET /v2/event-types?username={u}` | `2024-06-14` | **Corrected 2026-08-25**: returns `.data` as a **flat array** of event-type objects — personal types only. There is no `eventTypeGroups` and no `profiles`; the old claim that this reveals teams is stale. jq on the old shape fails with `Cannot index array with string "eventTypeGroups"`. |
| `GET /v2/event-types/{id}` | `2024-06-14` | `scheduleId`, `hidden`, `ownerId`, `minimumBookingNotice` (top-level int, **minutes**), `bookingWindow`, `confirmationPolicy` (see below) |
| `GET /v2/teams` | `2024-06-11` | `id`, `name`, `slug` |
| `GET /v2/teams/{teamId}/memberships` | `2024-06-11` | `userId`, `role`, `accepted`, `user.email` |
| `GET /v2/teams/{teamId}/event-types` | `2024-06-14` | **Added 2026-08-25 — required, not optional.** The username list above returns *only* personal event types; team event types are invisible there. Discover teams via `GET /v2/teams`, then list each team's event types here. |
| `GET\|PATCH /v2/teams/{teamId}/event-types/{id}` | `2024-06-14` | Team detail/update. Adds `schedulingType`, `hosts[]`, `assignAllTeamMembers` vs. the personal shape's `ownerId` + `users[]`. |
| `GET /v2/teams/{teamId}/event-types/{id}` | `2024-06-14` | **`schedulingType`**, `scheduleId`, **`hosts[]`** — the fields that explain the zeros |
| `GET /v2/calendars/google/connect` | `2024-06-11` | `.data.authUrl` — a Google consent URL |

### Endpoints that 404 — do not waste calls

**Verified 2026-08-21:** `/v2/credentials`, `/v2/apps`, `/v2/me/connected-calendars`,
`/v2/destination-calendars`. There is no API route that enumerates raw credentials, and none
observed that deletes a broken calendar connection — **removal is UI-only**, which is why the
disconnect-and-re-add remedy needs the user.

`/v2/calendars/busy-times` exists but requires a `calendarsToLoad` **array** parameter; without
it you get a 400 naming the field.

### About `authUrl`

`/v2/calendars/google/connect` returns a working Google OAuth URL, but its `state` token is
tied to the request and expires. For a human, **the UI path is more reliable**:
`https://app.cal.com/apps/installed/calendar`. Do not hand over the raw `authUrl` as the primary
instruction. Never paste it anywhere it would be logged — it carries `client_id` and `state`.

---

## `minimumBookingNotice` vs `confirmationPolicy` — these are NOT interchangeable

**Verified 2026-08-25** from Cal.com source, not inference — absent from this doc until now,
which cost a live incident's worth of design rework. Both fields sound like "advance notice"
controls; they enforce completely different things and **cannot deliver "blocked but
requestable" together.**

- **`minimumBookingNotice`** (top-level int, **minutes**, per event type) hides the slot from
  generation (`schedules/lib/slots.ts` clamps every range to `now + notice`) **and** hard-rejects
  a booking attempt inside the window with `HTTP 400 BookingTimeOutOfBounds`
  (`validateBookingTimeIsNotOutOfBounds.ts`), in the code path shared by the UI and the API. This
  check runs **before** any confirmation logic — set this large and `confirmationPolicy` becomes
  dead code for that window.
- **`confirmationPolicy`** is what actually delivers "slot visible, booking becomes a pending
  request." Shape (`cal-api-version: 2024-06-14`):

  ```json
  {
    "type": "time",
    "noticeThreshold": { "unit": "minutes", "count": 2880 },
    "blockUnconfirmedBookingsInBooker": true
  }
  ```

  `type` is `"always" | "time"` only — there is no `"disabled"` value for `type`; to turn it off
  send the separate shape `{"confirmationPolicy": {"disabled": true}}`.
  `blockUnconfirmedBookingsInBooker` is **required** whenever `type` is present. Use
  `unit: "minutes"`, not `"hours"` — the internal diff truncates, so an `hours` threshold behaves
  as "< N+1 hours," not "< N hours."
  A booking inside the threshold returns `HTTP 201` with `"status": "pending"` (confirmed live via
  a real booking + cancel on a hidden event type) — the Booker's own CTA still reads "Confirm",
  never "Request"; the only signal to the booker is a "Requires confirmation" badge that renders
  on *every* booking for that event type, not just in-window ones. Compensate in `description`
  copy if this distinction matters.
  Legacy names (`requiresConfirmation`, `requiresConfirmationThreshold`,
  `requiresConfirmationWillBlockSlot`) **do not exist in v2 responses** and are silently accepted
  and stripped on write — the v2 API bootstraps
  `ValidationPipe({whitelist: true})` **without** `forbidNonWhitelisted`, so an unknown field
  returns `HTTP 200` and changes nothing. **Always read the event type back after a PATCH; a 200
  is not evidence.**

- **`bookingFields` array-replace has an undocumented required-label trap.** The built-in
  `attendeePhoneNumber` field (`type: "phone"`) round-trips fine on GET with no `label`, but
  **PATCHing it back without an explicit `label` string returns HTTP 400** (`Validation failed
  for phone booking field: label must be a string`). Sending a single-field array otherwise
  succeeds and the API re-fills the other system defaults (email, location, title, notes, guests,
  rescheduleReason) — but not the phone field, confirming it needs its own explicit entry with a
  `label`. Fetch the live array first; do not hand-author it from a stale example.

- **Schedule creation requires `isDefault: boolean` explicitly** — `POST /v2/schedules` without it
  returns `HTTP 400 isDefault must be a boolean value` (`cal-api-version: 2024-06-11`).

---

## Public (unauthenticated) probes

Useful for confirming what a prospect actually sees, with no key.

**Verified 2026-08-21:**

- **Slug enumeration.** `https://cal.com/{username}` is a Next.js RSC page; the JSON is
  backslash-escaped. Grep `\\"slug\\":\\"[a-z0-9-]+\\"` — plain `"slug":"..."` matches nothing.
  This is how you catch stale slugs: a `404` on `cal.com/{user}/{slug}` means the slug is wrong,
  not that availability broke.
- **tRPC slots.** `https://cal.com/api/trpc/slots/getSchedule?input=<urlencoded JSON>`. Three
  gotchas, each returning a different unhelpful error:
  - A non-browser User-Agent gets **403** from Cloudflare. Send a real Chrome UA.
  - `duration: null` fails Zod validation — pass a **string** (`"30"`) or omit with the
    `meta.values` undefined-marker form.
  - `usernameList: []` is rejected for personal events; team events need `isTeamEvent: true`
    plus `eventTypeId`.
- An empty `slots: {}` is a genuine "nothing available" — Cal.com omits empty days rather than
  returning them as empty arrays, so absence of keys is the signal.

---

## Google Calendar MCP

**Verified 2026-08-21**, tools `mcp__claude_ai_Google_Calendar__*`:

- **`list_events` blows the token cap** on windows of ~6 weeks on a busy calendar (~200 events →
  ~110–200KB). The result is auto-saved to a file under the session's `tool-results/`; parse it
  with `jq`/python rather than re-reading it into context. Narrow with `fullText` when you only
  need a subset.
- **`fullText` is a verbatim AND match** across title, description, location, attendees.
  Matching on a marker string in the *description* is a far more precise filter than a title
  substring, and it is the right way to isolate machine-generated events.
- **`eventType` must be requested explicitly.** Omitting it silently excludes
  `WORKING_LOCATION` and `BIRTHDAY`. Those are `transparent` anyway, so for availability work
  the default is usually what you want — just know they are missing.
- **`delete_event` returns the full event with `status: "cancelled"`** on success, which is a
  usable per-item receipt. Set `notificationLevel: "NONE"` so nothing emails out.
- **Transient `The service is currently unavailable.`** — hit 3 times across 126 deletes.
  Not fatal and not a permissions problem; retry the individual id.
- **Parallel batches of ~20 delete calls in one message work fine.** That is the practical way
  to do a bulk purge, since no batch-delete tool exists.
- **`transparency` is absent on busy events** and set to `"transparent"` on free ones. Treat
  missing as opaque/busy.
- Events created by an API client show `creator.self: true` with **no `iCalUID`** — a useful tell
  for "this was written by automation," alongside a marker in the description.

### Deleting in bulk safely

1. Filter on **two** independent signals (e.g. a description marker **and** a title prefix) and
   assert the false-positive count is zero before deleting anything.
2. Write a restore manifest — ids, titles, start/end — to a durable path with `chmod 600`.
   Session temp directories get cleaned.
3. Confirm afterward with the same filter returning nothing, and with a
   before/after free-hours comparison per day.

---

## Environment caveats

- **`gcloud`** may be unusable against your company's Workspace data — an org can block the
  scopes.
- Do not plan around a local Google Calendar API reconcile script: it needs OAuth client files
  you may not have, and it is superseded anyway — see the anti-pattern section in SKILL.md.

---

## `GET /v2/calendars/busy-times` — reading a calendar you have no direct access to

**Verified 2026-08-21.** `cal-api-version: 2024-06-11`. The single most useful endpoint for
locating a bad event on a calendar your own tooling cannot read.

Required repeated params, one index per calendar:

```
calendarsToLoad[0][credentialId]=<int>
calendarsToLoad[0][externalId]=<url-encoded calendar id / email>
```

plus `loggedInUsersTz`, `dateFrom`, `dateTo` (`YYYY-MM-DD`).

Gotchas:
- **`curl -g` is mandatory.** Without globoff, `[0]` is read as a glob range and curl fails with
  `bad range in URL position N` before any request is sent.
- Omitting `calendarsToLoad` returns a 400 that names the field (`must be an array`).
- **Query one calendar per request.** Passing all of them merges the result and destroys the
  attribution you are trying to get.
- Returns `{start,end}` spans in **UTC**; convert before comparing against a local-time symptom.
- It returns busy *spans*, not events — no titles or ids. Enough to say "a 340h block runs
  Aug 26 → Sep 9 on this calendar," which is enough for a human to find and delete it.

Source of `credentialId` / `externalId`:

```bash
jq -r '.data.connectedCalendars[] | (.calendars // [])[]
       | select(.isSelected==true) | "\(.credentialId) \(.externalId)"' calendars.json
```

Note `credentialId` also appears at the connection level; the per-calendar one is what this
endpoint wants. Only `isSelected: true` calendars affect availability — read-only and
unselected ones are listed but ignored.

---

## Turning a calendar off — `/v2/selected-calendars`

**Verified 2026-08-21.** The emergency lever when a calendar you cannot edit is poisoning
availability. Only `isSelected: true` calendars feed conflict checking, and selection is
writable by API even though **`GET /v2/selected-calendars` 404s** — there is no read route, so
confirm state via `GET /v2/calendars` instead.

```bash
# cal-api-version: 2024-06-14 — returns 200 and takes effect immediately
curl -X DELETE -g \
  "https://api.cal.com/v2/selected-calendars?credentialId=<id>&externalId=<urlenc>&integration=google_calendar"
```

`POST` the same shape re-selects it. Reversible in one call per calendar.
**`POST` does NOT take the same shape — corrected 2026-09-11.** DELETE takes query
parameters; POST takes a **JSON body** and ignores the query string, returning
`400 "integration must be a string"` if you send the DELETE shape:

```bash
# cal-api-version: 2024-06-14 — returns 201
curl -X POST "https://api.cal.com/v2/selected-calendars" \
  -H "Content-Type: application/json" \
  -d '{"integration":"google_calendar","externalId":"<email>","credentialId":<int>}'
```

Reversible in one call per calendar. A small wrapper of your own (e.g. `calsel.sh on|off|dest|show`)
that covers both shapes and reads state back after every write is worth having.

**Setting the booking destination works too** (the 404 list above is about enumerating and
deleting credentials, not this): `PUT /v2/destination-calendars`, `cal-api-version: 2024-06-11`,
JSON body `{"integration":"google_calendar","externalId":"<email>"}` — returns 200. Verified
2026-09-11 moving the destination from one work calendar to another.

**This is a mutation, not a probe.** It has no dry-run and no confirmation step. A call made to
"see if the endpoint exists" silently changes live availability — do not send it exploratively.

**Know the cost before you pull it.** Deselecting stops the calendar's *real* busy times counting
too, so the booking page becomes over-available for anything that lived only there. Use it when
the phantom blocks outweigh the real commitments, and say plainly that conflict protection from
that calendar is gone until it is re-selected.

### Preferred fix instead: borrow access via calendar ACL

You can read **any** calendar the authenticated Google user has an ACL on, even one absent from
`list_calendars` — just pass its id as `calendarId`. Check the returned **`accessRole`**:

- `freeBusyReader` / `reader` → you can enumerate event **ids and times** but not titles, and
  **delete fails** with `The caller does not have permission`.
- `writer` / `owner` → you can delete.

So the minimal-permission fix for "phantom events on a calendar I cannot edit" is to have the
owner share that calendar with your authenticated account at **"Make changes to events"**. Then
delete precisely and re-select the calendar, keeping real conflict checking intact. That is
strictly better than deselecting, and it is the same amount of human clicking.
