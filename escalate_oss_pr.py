"""SEB -> Klaus: OSS credibility PR readiness escalation for NVIDIA/garak issue #713.

Builds the rationale + diff, routes through notify.py (queued locally if no
Telegram creds -- honest, no fake send). NO git push happens here.

IMPORTANT CONTEXT (honesty re prior run):
  A previous SEB run picked garak issue #219 and wrote a PII-extraction
  probe+detector. That pick is CONTESTED and was NOT safe to escalate as
  "unclaimed": issue #219 has an open DRAFT PR (#1407), an active contributor
  (frangelbarrera) who posted a detailed plan 2026-07-08, and garak already
  ships ProPILE PII extraction in garak/probes/propile.py. garak's own
  AGENTS.md BANS duplicate code-agent PRs and says to fail-closed. Escalating
  #219 as "clean / zero PRs" would have been dishonest (SOUL.md S5) and risked
  an auto-ban. Those files were removed.
  L1B3RT4S is elder-plinius/L1B3RT4S -- a prompt DATASET, not a code project
  with a PR workflow, so it is not a viable "open a credibility PR" target.

  This run pivots to issue #713 (tests: check plugin modules for classes not
  picked up by plugin enumeration) -- genuinely UNASSIGNED, no linked PR, fully
  offline, and directly in garak's requested test-gap work.
"""

import os
import sys
import json
import subprocess

SEB = r"C:\Users\mbapt\src\seb"
GARAK = os.path.join(SEB, "oss-work", "garak")
sys.path.insert(0, SEB)

TEST_FILE = "tests/plugins/test_plugin_enumeration_coverage.py"


def read_file(relpath):
    p = os.path.join(GARAK, relpath)
    with open(p, "r", encoding="utf-8") as fh:
        return fh.read()


def git_diff_new_file(relpath):
    """Produce a reviewable new-file diff (dev-null -> file)."""
    p = os.path.join(GARAK, relpath)
    out = subprocess.run(
        ["git", "--no-pager", "diff", "--no-index", os.devnull, p],
        cwd=GARAK,
        capture_output=True,
        text=True,
    )
    return (out.stdout or out.stderr).replace(os.devnull, "/dev/null")


test_src = read_file(TEST_FILE)
diff = git_diff_new_file(TEST_FILE)

EVENT = "oss-pr-ready-for-review"
TITLE = "garak #713 - plugin-enumeration coverage regression test (credibility PR, awaiting review)"

message = """SEB OSS CREDIBILITY PR - READY FOR YOUR REVIEW (do NOT open yet)

TARGET: NVIDIA/garak  issue #713 "tests: check plugin modules for classes that
aren't picked up by plugin enumeration"
WHY THIS ISSUE (genuinely unclaimed + requested test gap):
- Issue #713 is UNASSIGNED (no assignees) and has NO linked open PR (verified:
  `gh pr list --search "713 in:body"` returns only an unrelated #975 PR).
- It is a TEST-GAP task, exactly the "doc/test gaps" lane the mandate permits,
  and fully offline (no model/network) - safe under SOUL.md S5.
- I empirically scanned garak: 117 detector + 189 probe concrete classes, all
  currently enumerated (0 misses today). So the test is a REGRESSION GUARD:
  it will fail the moment someone adds a concrete plugin class that the
  enumeration misses (the exact gap #713 describes).

WHAT I BUILT (1 new file, no changes to existing code):
- tests/plugins/test_plugin_enumeration_coverage.py
  - Mirrors garak._plugins.PluginCache._enumerate_plugin_klasses discovery
    logic (scan non-dunder, non-underscore modules for concrete subclasses of
    the base plugin classes; excludes abstract mixins exactly as the real
    machinery does).
  - test_all_plugin_classes_are_enumerated[detectors|probes]: asserts every
    discovered concrete class is in enumerate_plugins().
  - test_enumeration_matches_discovery_count[detectors|probes]: asserts the two
    sets are equal (guards against inverse drift / stale plugin cache too).
  - British-english docstring, descriptive assert messages, parametrised per
    garak's AGENTS.md testing style.

VERIFICATION (run locally, read-only, no network):
- `pytest tests/plugins/test_plugin_enumeration_coverage.py` -> 4 passed (6.4s)
- NEGATIVE CONTROL PROVEN: monkeypatching enumerate_plugins to drop one real
  class (detectors.always.Pass) makes the test FAIL with:
  "concrete plugin classes in garak.detectors not picked up by plugin
   enumeration (see issue #713): ['detectors.always.Pass']"
  -> confirms the guard actually fires on a miss.
- Pre-existing FAILURE (NOT mine, reported honestly): the broader suite has one
  failing test, test_instantiate_probes[probes.audio.AudioAchillesHeel], because
  optional audio deps (soundfile, librosa) aren't installed here. My PR does
  not touch audio code; this failure exists independent of my change.

WHY NOT #219 / L1B3RT4S (honest pivot from a prior SEB run):
- Issue #219 (PII extraction) is CONTESTED: open DRAFT PR #1407, an active
  contributor who posted a detailed plan 2026-07-08, and garak already ships
  ProPILE PII extraction. garak's AGENTS.md BANS duplicate code-agent PRs, so
  escalating #219 as "unclaimed / zero PRs" would be false and risk a ban.
  The prior run's pii_extraction files were DELETED to avoid misleading this.
- L1B3RT4S (elder-plinius/L1B3RT4S) is a prompt DATASET, not a code repo with a
  PR workflow - not a viable credibility-PR target.

COMPLIANCE NOTES:
- SOUL.md S5 respected: only garak's offline test machinery used. No live
  model, no network, no unauthorized testing.
- NOT pushed. Per your handoff + garak AGENTS.md, this waits on YOUR sign-off
  before any PR is opened. When you approve, the eventual PR must include
  (per AGENTS.md): why not duplicating an existing PR (answer: #713 is
  unassigned, no linked PR), test commands+results, an explicit AI-assistance
  statement, and a Co-authored-by trailer.

NEXT: you review the diff, then tell me to open the PR (or adjust)."""

meta = {
    "label": "oss-pr-ready-for-review",
    "target_repo": "NVIDIA/garak",
    "issue": 713,
    "issue_title": "tests: check plugin modules for classes that aren't picked up by plugin enumeration",
    "files": [TEST_FILE],
    "tests_passed": 4,
    "negative_control": "proven: dropping detectors.always.Pass from enumeration makes the test FAIL",
    "known_unrelated_failure": "test_instantiate_probes[probes.audio.AudioAchillesHeel] (missing optional soundfile/librosa deps - pre-existing, not in this PR)",
    "pushed": False,
    "pivot_note": "Rejected prior #219 pick: contested (open PR #1407 + active claimer); L1B3RT4S is a dataset not a code repo.",
    "diffs": {TEST_FILE: diff},
}

from notify import escalate

result = escalate(EVENT, message, meta=meta)
print(json.dumps(result, indent=2))
print("ESCALATION_STATUS:", result["status"])
