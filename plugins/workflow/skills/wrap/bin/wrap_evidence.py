#!/usr/bin/env python3
"""wrap_evidence.py — the facts /wrap judges against. Filter, no writes.

    wrap_evidence.py <transcript.jsonl> [--no-git] [--no-gh]  > evidence.json

Emits one JSON object:
  session_id
  asks[]    — the user's own words, from all four channels a transcript carries them in:
                prompt   a main-chain user turn (plain text, or /command + its args)
                queued   a message they typed mid-turn (attachment.queued_command)
                feedback the text they gave when rejecting a tool call ("the user said:")
                decision their AskUserQuestion answers
              Harness noise is excluded: task notifications, local-command stdout,
              interrupt markers, system reminders, sidechain (subagent) turns.
  report    — the agent's last main-chain text message (what it claimed at the end)
  repos[]   — every git repo the session WROTE to (Edit/Write/NotebookEdit paths, and
              Bash commands that commit/push/open PRs), with branch, ahead/behind
              upstream and origin's default branch, dirty count, merged-into-default, and
              the PR (state, draft, named checks) when gh can see one.
              Reading a repo does not count as touching it.

Pure git/gh; no model. The dirty count is a fact about the checkout, which other sessions
may share — the evidence says so rather than attributing it.
"""
import json
import os
import re
import subprocess
import sys

NOISE_PREFIXES = ("<task-notification>", "<local-command-stdout>", "<local-command-stderr>",
                  "<local-command-caveat>", "[Request interrupted", "<system-reminder>",
                  "Caveat:", "Base directory for this skill:")
# built-in session controls, not requests for work
CONTROL_CMDS = {"clear", "compact", "model", "login", "logout", "exit", "config", "fast",
                "effort", "mcp", "rename", "rn", "resume", "status", "cost", "help",
                "permissions", "output-style", "context", "usage", "upgrade", "doctor"}
CMD_RE = re.compile(r"<command-name>/?([^<]+)</command-name>")
ARGS_RE = re.compile(r"<command-args>(.*?)</command-args>", re.S)
FEEDBACK_MARK = "the user said:\n"
DECISION_MARK = "Your questions have been answered:"
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
GIT_WRITE_RE = re.compile(r"\bgit\b[^\n;&|]*\b(commit|push)\b|\bgh\s+pr\s+(create|merge|ready)\b")
CD_RE = re.compile(r"(?:^|[;&|(]\s*)cd\s+(\"[^\"]+\"|'[^']+'|[^\s;&|)]+)")
GIT_C_RE = re.compile(r"\bgit\s+-C\s+(\"[^\"]+\"|'[^']+'|[^\s;&|]+)")
MAX_ASK = 2000


def _text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


def _tool_result_text(block):
    c = block.get("content")
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
    return c if isinstance(c, str) else ""


def _clean_prompt(text):
    """User-turn text -> the ask, or None if it is harness noise."""
    t = text.strip()
    if not t or t.startswith(NOISE_PREFIXES):
        return None
    m = CMD_RE.search(t)
    if m:
        name = m.group(1).strip().lstrip("/")
        if name in CONTROL_CMDS:
            return None
        args = ARGS_RE.search(t)
        a = args.group(1).strip() if args else ""
        return f"/{name} {a}".strip()
    # strip trailing system-reminder blocks the harness appends to a prompt
    t = re.sub(r"<system-reminder>.*?</system-reminder>", "", t, flags=re.S).strip()
    return t or None


def _expand(p, cwd):
    p = p.strip("\"'")
    p = os.path.expanduser(p)
    return p if os.path.isabs(p) else os.path.normpath(os.path.join(cwd or "/", p))


def parse(lines):
    """Transcript lines -> (session_id, asks, report, write_paths)."""
    sid, asks, report, paths = None, [], None, []
    seen_queued = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("isSidechain"):
            continue
        sid = sid or d.get("sessionId")
        ts = d.get("timestamp")
        cwd = d.get("cwd")
        att = d.get("attachment")
        if isinstance(att, dict) and att.get("type") == "queued_command":
            p = (att.get("prompt") or "").strip()
            if p and p not in seen_queued:
                seen_queued.add(p)
                asks.append({"channel": "queued", "ts": ts, "text": p[:MAX_ASK]})
            continue
        msg = d.get("message") or {}
        content = msg.get("content")
        if d.get("type") == "user":
            if isinstance(content, list) and any(
                    isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                for b in content:
                    if not (isinstance(b, dict) and b.get("type") == "tool_result"):
                        continue
                    t = _tool_result_text(b)
                    if FEEDBACK_MARK in t:
                        fb = t.split(FEEDBACK_MARK, 1)[1].strip()
                        if fb:
                            asks.append({"channel": "feedback", "ts": ts, "text": fb[:MAX_ASK]})
                    elif t.startswith(DECISION_MARK):
                        asks.append({"channel": "decision", "ts": ts,
                                     "text": t[len(DECISION_MARK):].strip()[:MAX_ASK]})
                continue
            ask = _clean_prompt(_text_of(content))
            if ask:
                asks.append({"channel": "prompt", "ts": ts, "text": ask[:MAX_ASK]})
        elif d.get("type") == "assistant" and isinstance(content, list):
            txt = _text_of(content).strip()
            if txt:
                report = txt
            for b in content:
                if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                    continue
                inp = b.get("input") or {}
                name = b.get("name")
                if name in WRITE_TOOLS:
                    fp = inp.get("file_path") or inp.get("notebook_path")
                    if fp:
                        paths.append(_expand(fp, cwd))
                elif name == "Bash":
                    cmd = inp.get("command") or ""
                    if GIT_WRITE_RE.search(cmd):
                        targets = [m.group(1) for m in GIT_C_RE.finditer(cmd)] or \
                                  [m.group(1) for m in CD_RE.finditer(cmd)]
                        if targets:
                            paths.extend(_expand(t, cwd) for t in targets)
                        else:
                            paths.append(cwd or "")
    for i, a in enumerate(asks, 1):
        a["i"] = i
    return sid, asks, report, [p for p in paths if p]


def _run(args, cwd=None, timeout=20):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def toplevel(path):
    d = path if os.path.isdir(path) else os.path.dirname(path)
    while d and not os.path.isdir(d):
        d = os.path.dirname(d)
    return _run(["git", "-C", d, "rev-parse", "--show-toplevel"]) if d else None


def _counts(top, rng):
    out = _run(["git", "-C", top, "rev-list", "--left-right", "--count", rng])
    if not out:
        return None
    behind, ahead = (int(x) for x in out.split())
    return {"ahead": ahead, "behind": behind}


def repo_facts(top, use_gh=True):
    f = {"path": top}
    branch = _run(["git", "-C", top, "rev-parse", "--abbrev-ref", "HEAD"])
    f["branch"] = branch
    default = _run(["git", "-C", top, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"]) \
        or "origin/main"
    f["default"] = default
    f["vs_default"] = _counts(top, f"{default}...HEAD")
    f["vs_upstream"] = _counts(top, "@{u}...HEAD")
    f["upstream"] = _run(["git", "-C", top, "rev-parse", "--abbrev-ref", "@{u}"])
    porcelain = _run(["git", "-C", top, "status", "--porcelain"])
    f["dirty_files"] = len(porcelain.splitlines()) if porcelain else 0
    f["dirty_note"] = "checkout may be shared; dirty files are not attributed to this session"
    f["pr"] = None
    if use_gh and branch and branch != "HEAD":
        out = _run(["gh", "pr", "list", "--head", branch, "--state", "all", "--limit", "1",
                    "--json", "number,state,isDraft,url,statusCheckRollup"], cwd=top)
        if out:
            try:
                prs = json.loads(out)
            except ValueError:
                prs = []
            if prs:
                p = prs[0]
                checks = [{"name": c.get("name") or c.get("context"),
                           "result": c.get("conclusion") or c.get("state")}
                          for c in (p.get("statusCheckRollup") or [])]
                f["pr"] = {"number": p.get("number"), "state": p.get("state"),
                           "draft": p.get("isDraft"), "url": p.get("url"),
                           "named_checks": checks}
    f["branch_state"] = branch_state(f)
    return f


def branch_state(f):
    """merged | on-default | nothing-ahead | unpushed | pushed — from facts only.

    0-ahead-of-default is ambiguous (fresh branch, or merged by squash/rebase), so only a
    MERGED PR earns "merged"; otherwise it is reported as nothing-ahead, never guessed.
    """
    pr = f.get("pr") or {}
    if pr.get("state") == "MERGED":
        return "merged"
    default = f.get("default") or ""
    if f.get("branch") and default.endswith("/" + f["branch"]):
        return "on-default"
    vd, vu = f.get("vs_default"), f.get("vs_upstream")
    if vd and vd["ahead"] == 0:
        return "nothing-ahead"
    if not f.get("upstream"):
        return "unpushed"
    return "unpushed" if vu and vu["ahead"] > 0 else "pushed"


def build(lines, use_git=True, use_gh=True):
    sid, asks, report, paths = parse(lines)
    repos = []
    if use_git:
        tops = []
        for p in paths:
            t = toplevel(p)
            if t and t not in tops:
                tops.append(t)
        repos = [repo_facts(t, use_gh) for t in tops]
    return {"session_id": sid, "asks": asks, "report": report, "repos": repos,
            "write_paths": sorted(set(paths))}


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    with open(args[0], encoding="utf-8", errors="replace") as fh:
        ev = build(fh, use_git="--no-git" not in argv, use_gh="--no-gh" not in argv)
    json.dump(ev, sys.stdout, indent=1)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
