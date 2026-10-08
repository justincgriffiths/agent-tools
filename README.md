# agent-tools

Claude Code skills that encode *judgment* — when to act, what to watch for, what a check can't
catch — extracted from day-to-day agent-assisted work. Each skill keeps the gotchas that cost
time the first time around.

## Install

```
/plugin marketplace add justincgriffiths/agent-tools
/plugin install workflow@jg-tools
```

Skills run namespaced, e.g. `/workflow:wrap`. No GitHub SSH key? Set
`CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` before adding the marketplace.

## Updates

Turn on auto-update once: `/plugin` → **Marketplaces** → `jg-tools` → **Enable auto-update**.
Or run `/plugin marketplace update jg-tools`. The plugin carries no `version`, so installs track
`main`. Changes are listed in [CHANGELOG.md](CHANGELOG.md).

## Skills

| Skill | Use it to |
|---|---|
| `learn` | Turn a correction or hard-won lesson into a durable rule in the right place |
| `wrap` | Close a session cleanly: capture, commit, hand off |
| `dedupe` | Find and resolve duplicate files/docs without losing the canonical copy |
| `doc-maintenance` | Keep docs and indexes honest as the code under them moves |
| `write-work-items` | Write tasks a human reviewer can actually act on |
| `naming` | Adopt one naming + frontmatter grammar across skill/script/template libraries |
| `unstick-prs` | Find PRs where finished work is dying and get them mergeable |
| `find-meeting-time` | Find a slot across calendars without the usual timezone/ownership traps |
| `booking-availability` | Audit and fix booking-page availability (Cal.com-style) |

## Contributing

Issues and PRs welcome; they're reviewed by hand. Licensed MIT.
