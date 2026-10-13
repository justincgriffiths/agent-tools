#!/usr/bin/env python3
"""Tests for bin/idea-doc-check.py. Run: python3 test/test-idea-doc-check.py"""
import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("chk", HERE.parent / "bin" / "idea-doc-check.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

TEMPLATE = (HERE.parent / "references" / "idea-doc.md").read_text()

COMPLETE = """# Cost per client

_Started 2026-10-12 · mode: interactive · source: org/repo#1_

## Problem statement
The biggest card line has no client on it, so margin per client is unknowable.

## Decision log
| # | Decision | Chosen | Decided by | Round |
|---|---|---|---|---|
| D1 | Attribution rule | path only | carried (org/repo#1) | 0 |
| D2 | Report cadence | monthly | Sam | 1 |
| D3 | Sessions carry a cwd | yes | agent (fact) | 1 |

## Assumptions
| # | Assumption | Kill-power | Status |
|---|---|---|---|
| A1 | Session rows carry a cwd | high | known |

## Research
### R1 - cwd present (tests A1)
- Finding: 412 of 415 rows have cwd - source: sessions.jsonl - confidence: high

## Deliverables and timeline
| ID | Deliverable | Done means |
|---|---|---|
| D1 | Monthly cost-per-client table | Partner update shows it |

| Week of | Packages | Owner | Gate |
|---|---|---|---|
| 10-19 | P1 | agent (small) | - |

## Work packages
| ID | Deliverable | Goal | Tier | Est. min | Depends-on | Acceptance |
|---|---|---|---|---|---|---|
| P1 | D1 | Price table | small | 20 | - | Sept total within 5% of statement |
| P2 | D1 | Approve price source | human | 10 | P1 | Sam ticks the box |

## Dry-fire
P1 on small: asked 1 question (which statement), fixed inputs, re-fired.
Result: pass
"""


def swap(doc, section, body):
    head = f"## {section}"
    start = doc.index(head)
    nxt = doc.find("\n## ", start + len(head))
    return doc[:start] + head + "\n" + body + "\n" + (doc[nxt:] if nxt != -1 else "")


class IdeaDocCheck(unittest.TestCase):
    def test_complete_doc_passes(self):
        self.assertEqual(chk.check(COMPLETE), [])

    def test_template_is_incomplete(self):
        gaps = chk.check(TEMPLATE)
        self.assertTrue(any("pending" in g for g in gaps))
        self.assertIn("decision log has no decision the person made in this session", gaps)

    def test_carried_and_agent_rows_do_not_count(self):
        doc = COMPLETE.replace("| Sam |", "| carried (org/repo#1) |")
        self.assertIn("decision log has no decision the person made in this session", chk.check(doc))
        for who in ["agent (assumed, conf: high)", "Claude (fact)", "the agent", "AI"]:
            doc = COMPLETE.replace("| Sam |", f"| {who} |")
            self.assertIn("decision log has no decision the person made in this session",
                          chk.check(doc), who)

    def test_person_named_like_agent_prefix_counts(self):
        self.assertEqual(chk.check(COMPLETE.replace("| Sam |", "| Aisha |")), [])

    def test_decided_by_found_by_header(self):
        log = ("| Decision | Chosen | Decided by | Round |\n|---|---|---|---|\n"
               "| Cadence | monthly | agent (fact) | 1 |\n")
        self.assertIn("decision log has no decision the person made in this session",
                      chk.check(swap(COMPLETE, "Decision log", log)))

    def test_autopilot_needs_overturn_line(self):
        doc = COMPLETE.replace("mode: interactive", "mode: autopilot")
        self.assertIn("autopilot doc has no 'Overturned: N of M' line in the decision log", chk.check(doc))
        doc = doc.replace("| D3 | Sessions carry a cwd | yes | agent (fact) | 1 |",
                          "| D3 | Sessions carry a cwd | yes | agent (fact) | 1 |\n\nOverturned: 1 of 6")
        self.assertEqual(chk.check(doc), [])

    def test_timeline_table_required(self):
        body = "| ID | Deliverable | Done means |\n|---|---|---|\n| D1 | Table | shown |\n"
        self.assertIn("Deliverables and timeline needs two tables (deliverables, timeline)",
                      chk.check(swap(COMPLETE, "Deliverables and timeline", body)))

    def test_bad_tier_estimate_and_acceptance(self):
        doc = COMPLETE.replace("| small | 20 | - | Sept total within 5% of statement |",
                               "| Opus probably | a few hours | - | - |")
        gaps = chk.check(doc)
        self.assertTrue(any("tier 'Opus probably'" in g for g in gaps))
        self.assertTrue(any("Est. min 'a few hours'" in g for g in gaps))
        self.assertIn("package P1: no acceptance check", gaps)

    def test_package_table_needs_tier_column(self):
        body = "| ID | Goal |\n|---|---|\n| P1 | x |\n"
        self.assertIn("Work packages has no package table with a Tier column",
                      chk.check(swap(COMPLETE, "Work packages", body)))

    def test_dry_fire_needs_result(self):
        doc = COMPLETE.replace("Result: pass", "Went fine.")
        self.assertIn("Dry-fire has no 'Result: pass' or 'Result: re-tiered to <tier>' line", chk.check(doc))
        self.assertEqual(chk.check(COMPLETE.replace("Result: pass", "Result: re-tiered to mid because inputs were ambiguous")), [])

    def test_missing_section_and_case(self):
        self.assertIn("missing section: ## Dry-fire", chk.check(COMPLETE.replace("## Dry-fire", "## Later")))
        self.assertEqual(chk.check(COMPLETE.replace("## Decision log", "## Decision Log")), [])

    def test_pending_inside_comment_ignored(self):
        self.assertEqual(chk.check(COMPLETE + "\n<!-- _pending_ -->\n"), [])


if __name__ == "__main__":
    unittest.main()
