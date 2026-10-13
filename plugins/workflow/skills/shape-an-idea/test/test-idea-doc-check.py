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

COMPLETE = """# Inbox digest

## Problem statement
Ops leads miss client asks buried in long threads; a daily digest surfaces them.

## Decision log
| # | Decision | Chosen | Decided by | Round |
|---|---|---|---|---|
| D1 | Audience | Ops leads only | Sam | 1 |
| D2 | Mail API supports labels | yes | agent (fact) | 1 |

## Assumptions
| # | Assumption | Kill-power | Status |
|---|---|---|---|
| A1 | Asks are detectable from text | high | known |

## Research plan and findings
### R1 - detectability (tests A1)
- Finding: 18 of 20 sampled asks had an imperative verb - source: sample.csv - confidence: med

## Workflow v0
| Step | Input | Output | Who |
|---|---|---|---|
| 1 | inbox | threads | script |

## Next moves
1. Run on 10 days of mail
"""


class IdeaDocCheck(unittest.TestCase):
    def test_template_is_incomplete(self):
        gaps = chk.check(TEMPLATE)
        self.assertTrue(any("pending" in g for g in gaps))
        self.assertIn("decision log has no decision made by a person", gaps)

    def test_complete_doc_passes(self):
        self.assertEqual(chk.check(COMPLETE), [])

    def test_agent_only_decisions_fail(self):
        doc = COMPLETE.replace("| Sam |", "| agent (fact) |")
        self.assertIn("decision log has no decision made by a person", chk.check(doc))

    def test_missing_section(self):
        doc = COMPLETE.replace("## Next moves", "## Later")
        self.assertIn("missing section: ## Next moves", chk.check(doc))

    def test_pending_inside_comment_ignored(self):
        doc = COMPLETE + "\n<!-- _pending_ -->\n"
        self.assertEqual(chk.check(doc), [])

    def test_workflow_needs_table(self):
        doc = COMPLETE.replace("| Step | Input | Output | Who |\n|---|---|---|---|\n| 1 | inbox | threads | script |",
                               "Do the thing.")
        self.assertIn("Workflow v0 has no step table", chk.check(doc))

    def test_next_moves_need_items(self):
        doc = COMPLETE.replace("1. Run on 10 days of mail", "Later.")
        self.assertIn("Next moves has no list items", chk.check(doc))


if __name__ == "__main__":
    unittest.main()
