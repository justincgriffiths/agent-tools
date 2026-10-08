#!/usr/bin/env python3
"""Offline tests for receipts-check.py. No network: the judge and the redactor are fake commands.
Run: python3 unstick-prs/test/test-receipts-check.py"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "..", "bin")
SCRIPT = os.path.join(BIN, "receipts-check.py")


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


rc = load("receipts-check")

JSON_CHECKS = json.dumps([
    {"name": "build", "state": "COMPLETED", "conclusion": "SUCCESS"},
    {"name": "test", "state": "COMPLETED", "conclusion": "FAILURE"},
])
TEXT_CHECKS = (
    "build\tpass\t1m02s\thttps://x/1\n"
    "test\tfail\t3m10s\thttps://x/2\n"
)


class ParseChecks(unittest.TestCase):
    def test_json_form(self):
        got = rc.parse_checks(JSON_CHECKS)
        self.assertEqual(len(got), 2)
        self.assertEqual(got[0]["name"], "build")

    def test_text_form(self):
        got = rc.parse_checks(TEXT_CHECKS)
        self.assertEqual([c["name"] for c in got], ["build", "test"])

    def test_empty_is_empty(self):
        self.assertEqual(rc.parse_checks(""), [])
        self.assertEqual(rc.parse_checks("   \n  \n"), [])
        self.assertEqual(rc.parse_checks("[]"), [])

    def test_non_list_json_falls_back_to_text(self):
        # {"not": "a list"} is valid JSON but not a checks array -> treated as one text line
        got = rc.parse_checks('{"not": "a list"}')
        self.assertEqual(len(got), 1)


class BuildStateAndQuestions(unittest.TestCase):
    def test_build_state_caps_body(self):
        checks = json.loads(JSON_CHECKS)
        s = rc.build_state(checks, "y" * 20000)
        d = json.loads(s)
        self.assertEqual(d["n_checks"], 2)
        self.assertLessEqual(len(d["pr_body"]), rc.MAX_BODY)

    def test_questions_shape(self):
        qs = rc.questions()
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0]["type"], "yes_no")
        self.assertEqual(qs[0]["id"], "receipts")


class EndToEnd(unittest.TestCase):
    """Runs the CLI with a fake judge and a fake redactor, no network, temp dirs only."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.fake = os.path.join(self.tmp, "fake-judge.py")
        with open(self.fake, "w") as f:
            f.write(
                "import json,sys,os\n"
                "req=json.load(sys.stdin)\n"
                "open(os.environ['CAPTURE'],'w').write(json.dumps(req))\n"
                "mode=os.environ.get('FAKE_MODE','ok')\n"
                "if mode=='fail': sys.exit(4)\n"
                "vs=[]\n"
                "for q in req['questions']:\n"
                "  if mode=='down':\n"
                "    vs.append({'id':q['id'],'escalate':True,'reason':'unreachable',"
                "'hint':'unreachable'}); continue\n"
                "  a=0.9 if mode=='claimed_only' else 0.1\n"
                "  vs.append({'id':q['id'],'type':q['type'],'answer':a,'confidence':0.9,"
                "'escalate':False})\n"
                "print(json.dumps({'verdicts':vs,'model':'fake','latencyMs':5,'usage':{}}))\n")
        self.redactor = os.path.join(self.tmp, "redact.py")
        with open(self.redactor, "w") as f:
            f.write("import sys; sys.stdout.write(sys.stdin.read().replace('SECRETCLIENT','<client>'))\n")
        self.capture = os.path.join(self.tmp, "req.json")
        self.log = os.path.join(self.tmp, "scratch.jsonl")
        self.checks_file = os.path.join(self.tmp, "checks.json")
        with open(self.checks_file, "w") as f:
            f.write(JSON_CHECKS)
        self.body_file = os.path.join(self.tmp, "body.txt")
        with open(self.body_file, "w") as f:
            f.write("## Verification\nRan for SECRETCLIENT: tests pass (self-reported).\n")

    def run_cli(self, checks_file=None, body_file=None, extra_args=(), **env):
        e = dict(os.environ, JUDGE_CMD=f"{sys.executable} {self.fake}", JUDGE_REDACT=self.redactor,
                 CAPTURE=self.capture, JUDGE_LOG=self.log, **env)
        args = [sys.executable, SCRIPT]
        if checks_file is not None:
            args += ["--checks", checks_file]
        if body_file is not None:
            args += ["--body", body_file]
        args += list(extra_args)
        stdin_text = "" if checks_file else JSON_CHECKS
        return subprocess.run(args, input=stdin_text, capture_output=True, text=True, env=e)

    def test_nonempty_checks_exit_0(self):
        r = self.run_cli(checks_file=self.checks_file, body_file=self.body_file, extra_args=["--pr", "94"])
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_zero_checks_exit_1_clear_message(self):
        empty = os.path.join(self.tmp, "empty.json")
        with open(empty, "w") as f:
            f.write("[]")
        r = self.run_cli(checks_file=empty, body_file=self.body_file)
        self.assertEqual(r.returncode, 1)
        self.assertIn("empty rollup is not green", r.stderr)

    def test_checks_via_stdin(self):
        r = self.run_cli(body_file=self.body_file)  # no --checks -> JSON_CHECKS via stdin
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_shadow_verdict_logged_and_redacted(self):
        r = self.run_cli(checks_file=self.checks_file, body_file=self.body_file, extra_args=["--pr", "94"])
        self.assertEqual(r.returncode, 0)
        row = json.loads(open(self.log).read().strip())
        self.assertEqual((row["site"], row["mode"], row["pr"]),
                         ("unstick-prs:receipts", "shadow", "94"))
        self.assertIn("receipts", row["answers"])
        sent = open(self.capture).read()
        self.assertNotIn("SECRETCLIENT", sent)
        self.assertIn("<client>", sent)

    def test_no_body_skips_shadow_but_gate_still_runs(self):
        r = self.run_cli(checks_file=self.checks_file)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(self.log))

    def test_zero_checks_still_attempts_shadow(self):
        empty = os.path.join(self.tmp, "empty.json")
        with open(empty, "w") as f:
            f.write("[]")
        r = self.run_cli(checks_file=empty, body_file=self.body_file)
        self.assertEqual(r.returncode, 1)
        self.assertTrue(os.path.exists(self.log))

    def test_judge_failure_is_non_fatal_gate_still_decides(self):
        r = self.run_cli(checks_file=self.checks_file, body_file=self.body_file, FAKE_MODE="fail")
        self.assertEqual(r.returncode, 0, r.stderr)
        row = json.loads(open(self.log).read().strip())
        self.assertIn("error", row)

    def test_no_judge_configured_skips_shadow_gate_still_decides(self):
        e = {k: v for k, v in os.environ.items() if not k.startswith("JUDGE_")}
        e.update(CAPTURE=self.capture, JUDGE_LOG=self.log, JUDGE_REDACT=self.redactor)
        r = subprocess.run([sys.executable, SCRIPT, "--checks", self.checks_file,
                           "--body", self.body_file], input="", capture_output=True, text=True, env=e)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(self.capture))
        self.assertFalse(os.path.exists(self.log))

    def test_missing_redactor_sends_nothing(self):
        e = dict(os.environ, JUDGE_CMD=f"{sys.executable} {self.fake}", JUDGE_REDACT="/nonexistent-xyz",
                 CAPTURE=self.capture, JUDGE_LOG=self.log)
        r = subprocess.run([sys.executable, SCRIPT, "--checks", self.checks_file,
                           "--body", self.body_file], input="", capture_output=True, text=True, env=e)
        self.assertEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(self.capture))
        row = json.loads(open(self.log).read().strip())
        self.assertIn("redactor missing", row["error"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
