# Records — the second grammar

Everything in `SKILL.md` §2 governs a **unit**: a thing you invoke or open by
name. A **record** is different — a row in a set, one of thousands, whose name
exists to be sorted, parsed and deduplicated by a machine. Records get a second
grammar, and it was already running in three places before it was written down.

| | Unit | Record |
|---|---|---|
| Separator | `-` throughout | `_` between **fields**, `-` **inside** a field |
| Example | `deck-to-pdf` | `acme_2026-08-15_email_prospects_promo_fall-sale_a` |
| Named for | a human reaching for it | a parser and a sort order |
| Lives in | the four libraries | campaign platforms, media trees, exports |

The two-level separator is the whole point: `_` delimits, `-` is ordinary
within-field spelling, so a field may hold a multi-word phrase without the
delimiter becoming ambiguous. **A record is a tuple, not a phrase.** Pure kebab
cannot express that, which is why a record written in unit grammar is
unparseable and a unit written in record grammar reads as machine output.

## The three live record grammars

Confirm which one you are in before writing a parser.

1. **Email-platform campaigns** — best enforced by a small naming library:
   `<client>_<iso-date>_<channel>_<audience>_<type>_<kebab-descriptor>_<variant>`,
   seven fields.
2. **Ad names** — a typical ad-platform convention: ` - ` delimited, 8–12
   segments, `XNA` as explicit not-applicable.
3. **Media files** — below.

Per-platform UTM parameter specs belong in their own conventions doc, not here.

## Two rules that look like violations and are not

**`XNA` is a value, not a null.** It means "deliberately not applicable", and
collapsing it to empty destroys the distinction between *unset* and
*chosen-as-none*. Lowercase it (`xna`) in a kebab context.

**The `<client>_` prefix breaks "do not encode the client" on purpose.** That
rule governs units — a skill belongs to a job, not a customer. In a record the
client prefix is *identity*: these names live in the client's own ad account
beside other agencies' work, and the prefix is what makes ours selectable. Keep
it in records; keep it out of unit names.

## Media and file records

`<iso-date>_<hhmm>_<device>_<original-stem>.<ext>`, lowercase extension.

```
2016-07-09_2101_iphone-6s_img-5689.mov
2023-08-05_2056_iphone-13-mini_img-3151.mov
2025-10-16_2307_pixel_pxl-20251016-230653604.mp4
```

Four rules, all of them paid for:

1. **Date first, always.** It is what makes the set collision-free and
   chronologically sortable in any browser. One 64-file batch already contained
   `IMG_3385` twice — a 2019 iPhone XS and a 2025 iPhone 16 Pro. Camera counters
   recycle; dates do not.
2. **Keep the original stem as the last field.** It is the only link back to the
   source and it disambiguates same-minute captures. This is the record
   equivalent of `source:` — but a file has no frontmatter, so its name carries
   the provenance.
3. **Local time, with the offset verified.** Never name from a UTC timestamp.
   iPhone video carries `CreateDate` in UTC *and* `Keys:CreationDate` in local
   time with a real offset; naming from the former files an evening clip under
   the next day and splits one evening across two dates. Android/Pixel appears
   to write local time into `CreateDate`, so treating it as UTC breaks it the
   other way. Where the offset is genuinely unknown, record it as unknown — do
   not synthesise one from the host's timezone, and never pass
   `-api QuickTimeUTC`, which does exactly that.
4. **The event is a folder, not a filename field.** `<year>/<date>-<event>/`. So
   a label can be added later by *moving* a file, never renaming it — the
   recorded checksum still matches. And an unlabelled date is a valid state
   rather than a field demanding `xna`.

Device comes from `Model`, falling back to `pixel` for `PXL_*`, else `xna`.

*Judgment:* the event label itself. Nothing derives it. A capture-date cluster
is not an event, and an export batch is emphatically not one — a single download
spanned 2015–2025. Labels come from a human-maintained `media-events.tsv`
(`<iso-date><tab><slug>`), the only source. A confident wrong guess propagates
into every filename and folder it touches; a first attempt read one evening
cluster as an event that actually happened years later.

*Checked:* the shape, by a rename planner that refuses to emit a name it cannot derive
a date for and flags a target collision rather than silently suffixing it. Per gotcha 2, the safe-rename set is
enumerated, never inferred.
