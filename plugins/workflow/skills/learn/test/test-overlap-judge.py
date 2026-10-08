#!/usr/bin/env python3
"""Offline tests for learn/scripts/overlap-judge.py. No network: the judge is a fake command;
redactor is a fake filter. Temp dirs for all writes.

Run: python3 learn/test/test-overlap-judge.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


jo = load("overlap_judge", os.path.join(SCRIPTS, "overlap-judge.py"))

SAMPLE = """\
NAME                   | LINES | RESOURCES          | DESCRIPTION (first ~40 words)
------------------------------------------------------------------------------------------------
gmail-rules-apply      |   80 | -                  | Apply proposed Gmail filter rules to the live inbox, one batch at a time, with a rollback plan and a verify step.
gmail-rules-propose    |   75 | -                  | Propose new Gmail filter rules by mining the inbox for repeated senders and subjects, ranked by volume.
gmail-rules-prune      |   60 | -                  | Prune stale Gmail filter rules that no longer match any recent mail, with a before/after count.
unrelated-skill        |  200 | reference/         | Build a client deck from a memo, following the house design system tokens end to end.
claude-md-inventory    |     - | (no SKILL.md)      | shared assets / not a triggerable skill
"""


class ParseRows(unittest.TestCase):
    def test_skips_header_separator_and_no_skillmd(self):
        rows = jo.parse_rows(SAMPLE)
        names = [r["name"] for r in rows]
        self.assertEqual(names, ["gmail-rules-apply", "gmail-rules-propose",
                                 "gmail-rules-prune", "unrelated-skill"])

    def test_description_captured(self):
        rows = jo.parse_rows(SAMPLE)
        apply_row = next(r for r in rows if r["name"] == "gmail-rules-apply")
        self.assertIn("rollback plan", apply_row["description"])


class CandidatePairs(unittest.TestCase):
    def test_gmail_rules_trio_pairs_on_shared_distinctive_words(self):
        rows = jo.parse_rows(SAMPLE)
        pairs = jo.candidate_pairs(rows)
        names_in_pairs = {(a, b) for _, a, b, _ in pairs}
        # the three gmail-rules-* skills share "gmail" + "filter" + "rules" (rare tokens in
        # this small corpus); the unrelated deck skill should not pair with any of them.
        self.assertIn(("gmail-rules-apply", "gmail-rules-propose"), names_in_pairs)
        self.assertIn(("gmail-rules-apply", "gmail-rules-prune"), names_in_pairs)
        self.assertIn(("gmail-rules-propose", "gmail-rules-prune"), names_in_pairs)
        self.assertFalse(any("unrelated-skill" in (a, b) for _, a, b, _ in pairs))

    def test_bounded_to_max_pairs(self):
        # Build a corpus where every description shares two rare words with every other —
        # C(30,2) = 435 candidate pairs before capping.
        rows = [{"name": f"skill-{i}", "description": f"zzqx wobbleflub skill number {i}"}
               for i in range(30)]
        pairs = jo.candidate_pairs(rows)
        self.assertLessEqual(len(pairs), jo.MAX_PAIRS)

    def test_no_shared_distinctive_words_no_pairs(self):
        rows = [{"name": "a", "description": "completely different topic alpha"},
                {"name": "b", "description": "another unrelated subject beta"}]
        self.assertEqual(jo.candidate_pairs(rows), [])


class BuildQuestions(unittest.TestCase):
    def test_shape(self):
        pairs = [(3, "a", "b", ["gmail", "filter", "rules"])]
        qs = jo.build_questions(pairs)
        self.assertEqual(qs[0]["id"], "pair_0")
        self.assertEqual(qs[0]["type"], "yes_no")
        self.assertIn("'a'", qs[0]["question"])
        self.assertIn("'b'", qs[0]["question"])
        self.assertIn("gmail", qs[0]["question"])
        # the shared-word hint lives in the question text, never in a criteria field.
        self.assertNotIn("criteria", qs[0])


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.fake = os.path.join(self.tmp, "fake-judge.py")
        with open(self.fake, "w") as f:
            f.write(
                "import json,sys\n"
                "req=json.load(sys.stdin)\n"
                "mode=__import__('os').environ.get('FAKE_MODE','ok')\n"
                "if mode=='fail': sys.exit(4)\n"
                "vs=[]\n"
                "for q in req['questions']:\n"
                "  if mode=='down': vs.append({'id':q['id'],'escalate':True,'reason':'unreachable'}); continue\n"
                "  vs.append({'id':q['id'],'answer':0.9,'escalate':False,'confidence':0.9})\n"
                "print(json.dumps({'verdicts':vs,'model':'fake','latencyMs':5,'usage':{}}))\n")
        self.redactor = os.path.join(self.tmp, "redact.py")
        with open(self.redactor, "w") as f:
            f.write("import sys; sys.stdout.write(sys.stdin.read())\n")
        self.log = os.path.join(self.tmp, "log.jsonl")

    def test_full_run_flags_and_logs(self):
        rc = jo.main([], stdin_text=SAMPLE, judge_cmd=f"{sys.executable} {self.fake}",
                     redactor=self.redactor, log_path=self.log)
        self.assertEqual(rc, 0)
        row = json.loads(open(self.log).read().strip())
        self.assertEqual((row["site"], row["mode"]), ("learn:overlap", "shadow"))

    def test_judge_down_still_exits_zero_no_log(self):
        rc = jo.main([], stdin_text=SAMPLE, judge_cmd=f"{sys.executable} {self.fake}",
                     redactor=self.redactor, log_path=self.log, ) if False else None
        # use env for FAKE_MODE
        os.environ["FAKE_MODE"] = "down"
        try:
            rc = jo.main([], stdin_text=SAMPLE, judge_cmd=f"{sys.executable} {self.fake}",
                        redactor=self.redactor, log_path=self.log)
        finally:
            del os.environ["FAKE_MODE"]
        self.assertEqual(rc, 0)
        self.assertFalse(os.path.exists(self.log))

    def test_unset_judge_cmd_skips(self):
        env = dict(os.environ, JUDGE_REDACT=self.redactor, JUDGE_LOG=self.log)
        env.pop("JUDGE_CMD", None)
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "overlap-judge.py")],
                           input=SAMPLE, capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0)
        self.assertIn("skipping", r.stdout)
        self.assertFalse(os.path.exists(self.log))

    def test_missing_redactor_exits_zero(self):
        rc = jo.main([], stdin_text=SAMPLE, judge_cmd=f"{sys.executable} {self.fake}",
                     redactor="/nonexistent", log_path=self.log)
        self.assertEqual(rc, 0)
        self.assertFalse(os.path.exists(self.log))

    def test_no_pairs_exits_zero(self):
        rc = jo.main([], stdin_text="NAME | LINES | RESOURCES | DESCRIPTION\n---\n",
                     judge_cmd=f"{sys.executable} {self.fake}", redactor=self.redactor,
                     log_path=self.log)
        self.assertEqual(rc, 0)

    def test_cli_subprocess_never_fails(self):
        """Real subprocess invocation via stdin, as a scheduled run would call it."""
        env = dict(os.environ, JUDGE_CMD=f"{sys.executable} {self.fake}",
                  JUDGE_REDACT=self.redactor, JUDGE_LOG=self.log)
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "overlap-judge.py")],
                           input=SAMPLE, capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0)
        self.assertIn("overlap-judge:", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)
