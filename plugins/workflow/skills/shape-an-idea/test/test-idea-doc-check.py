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

N=1 run: yesterday's inbox; step 1 missed forwarded threads.

## Next moves
1. Run on 10 days of mail
2. Script the label step
3. Ask two ops leads to read one digest
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
        doc = COMPLETE.replace("2. Script the label step\n", "")
        self.assertIn("Next moves has 2 list items; needs 3", chk.check(doc))

    def test_workflow_needs_n1_note(self):
        doc = COMPLETE.replace("N=1 run: yesterday's inbox; step 1 missed forwarded threads.", "")
        self.assertIn("Workflow v0 has no N=1 run note", chk.check(doc))

    def test_decided_by_found_by_header_not_position(self):
        log = ("| Decision | Chosen | Decided by | Round |\n|---|---|---|---|\n"
               "| Audience | Ops | agent (fact) | 1 |\n")
        doc = self._swap_log(log)
        self.assertIn("decision log has no decision made by a person", chk.check(doc))

    def test_second_table_header_not_counted(self):
        log = ("| # | Decision | Chosen | Decided by | Round |\n|---|---|---|---|---|\n"
               "| D1 | X | y | agent (fact) | 1 |\n\n### Waived\n"
               "| # | Decision | Chosen | Decided by | Round |\n|---|---|---|---|---|\n"
               "| D2 | Z | w | Claude (fact) | 2 |\n")
        self.assertIn("decision log has no decision made by a person", chk.check(self._swap_log(log)))

    def test_agent_name_variants(self):
        for who in ["Claude (fact)", "the agent", "AI (fact)", "Claude"]:
            doc = COMPLETE.replace("| Sam |", f"| {who} |")
            self.assertIn("decision log has no decision made by a person", chk.check(doc), who)

    def test_person_named_like_agent_prefix_counts(self):
        doc = COMPLETE.replace("| Sam |", "| Aisha |")
        self.assertEqual(chk.check(doc), [])

    def test_template_assumption_row_pending(self):
        self.assertIn("section still pending: ## Assumptions", chk.check(TEMPLATE))

    def test_heading_case_insensitive(self):
        doc = COMPLETE.replace("## Decision log", "## Decision Log")
        self.assertEqual(chk.check(doc), [])

    @staticmethod
    def _swap_log(log):
        start = COMPLETE.index("## Decision log")
        end = COMPLETE.index("## Assumptions")
        return COMPLETE[:start] + "## Decision log\n" + log + "\n" + COMPLETE[end:]


if __name__ == "__main__":
    unittest.main()
