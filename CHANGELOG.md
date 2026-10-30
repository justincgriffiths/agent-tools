# Changelog

## 2026-10-08
- Initial release: `workflow` plugin, 9 skills.

## 2026-10-08 (update)
- All 9 skills updated to the current upstream (six weeks of changes). learn/wrap/unstick-prs: the second-model check is now optional via `JUDGE_CMD`; learn adds `hookrefs.sh` and `overlap-judge.py`; naming adds the records/branches/sessions grammars and `rubric.py`.

## 2026-10-12
- New skill `shape-an-idea`: shapes a worthwhile but unspecified idea into deliverables, a timeline and tiered work packages (script/small/mid/frontier/human), proves one package with a dry-fire on its own tier, and has an autopilot mode that stops at gates and records an overturn rate. Ships with `idea-doc-check.py`, unit tests, and dry-run scenarios plus a rubric.
- Session-report issue form for sharing how a skill went on a real problem.

## 2026-10-30
- Every skill now has a README: when to use it, how to invoke it, an example, outputs and requirements. The skills table in the root README links to each one.
