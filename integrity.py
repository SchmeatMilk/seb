"""
SEB — integrity invariants.

Hard rule: SEB never records a claim it cannot substantiate. Every function here
FAILS LOUD AND CLOSED. A raised exception that stops a pipeline is always
preferable to a false row in the database or a false sentence in a client
document. This module exists because on 2026-08-01 the automation marked an
engagement 'completed' with zero findings and a dangling invoice reference.

See SEB_V2_MASTER_PLAN.md Part 0.
"""
from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from typing import Optional


class IntegrityViolation(Exception):
    """Raised when SEB is about to record something it cannot substantiate."""


@dataclass(frozen=True)
class AuthorizationRecord:
    company: str
    authorized_url: str
    scope: str
    granted: bool
    source_path: str


def load_verified_authorization(path: str) -> AuthorizationRecord:
    """Load an authorization, or refuse. There is no 'probably fine' branch.

    Replaces gauntlet.py's check that the token is merely a non-empty string
    (gauntlet.py:296-299), under which the literal 'SELF-AUTH-dogfood' passes.
    """
    if not path or not os.path.exists(path):
        raise IntegrityViolation(f"No authorization record at {path!r}")
    if "QUARANTINE" in path.replace("\\", "/").upper():
        raise IntegrityViolation(f"Quarantined authorization may never be used: {path!r}")

    with open(path, encoding="utf-8") as fh:
        rec = json.load(fh)

    if rec.get("written_authorization_granted") is not True:
        raise IntegrityViolation(f"{path}: written_authorization_granted is not True")

    url = rec.get("authorized_url", "")
    if not isinstance(url, str) or not url.startswith("http"):
        raise IntegrityViolation(
            f"{path}: missing/invalid 'authorized_url'. Free-text scope is not "
            f"machine-checkable and cannot gate a scan."
        )
    if not rec.get("provenance"):
        raise IntegrityViolation(
            f"{path}: missing 'provenance'. Every authorization must record how it "
            f"was obtained (countersigned email, signed PDF, DocuSign envelope id)."
        )

    return AuthorizationRecord(
        company=rec["company"],
        authorized_url=url,
        scope=rec.get("scope", ""),
        granted=True,
        source_path=path,
    )


def assert_target_in_scope(target_url: str, auth: AuthorizationRecord) -> None:
    """Scope-lock. A scan whose host differs from the authorized host is not authorized."""
    from urllib.parse import urlparse

    t, a = urlparse(target_url).netloc.lower(), urlparse(auth.authorized_url).netloc.lower()
    if not t or t != a:
        raise IntegrityViolation(
            f"SCOPE MISMATCH: target host {t!r} != authorized host {a!r} "
            f"(record: {auth.source_path}). Refusing to scan."
        )


def assert_engagement_completable(db_path: str, engagement_id: str) -> None:
    """An engagement may not be marked delivered without persisted findings and a report.

    This is the exact invariant violated on 2026-08-01 19:03.
    """
    con = sqlite3.connect(db_path)
    n = con.execute(
        "SELECT COUNT(*) FROM findings WHERE engagement_id=?", (engagement_id,)
    ).fetchone()[0]
    row = con.execute(
        "SELECT report_path FROM engagements WHERE id=?", (engagement_id,)
    ).fetchone()
    if n == 0:
        raise IntegrityViolation(
            f"{engagement_id}: 0 findings persisted. An engagement with no findings "
            f"has not been performed. (A clean result is still a finding row — "
            f"record it explicitly as 'no vulnerabilities detected'.)"
        )
    if not row or not row[0] or not os.path.exists(row[0]):
        raise IntegrityViolation(f"{engagement_id}: report_path missing or file absent")


def assert_no_unsubstantiated_capability_claim(text: str) -> None:
    """Block known-false capability claims from reaching a client.

    Every string here was verified false on 2026-08-01. Delete an entry ONLY when
    the corresponding capability is genuinely proven by a passing test.
    """
    FALSE_CLAIMS = {
        "100+ probes": "garak/PyRIT/Giskard have never fired; runs are L1B3RT4S-only (74 probes).",
        "4 tools": "Only 1 attack tool (L1B3RT4S) has ever executed.",
        "200+ probes": "Not achieved.",
        "Signed authorization on file": (
            "Must never be asserted by a template. Only integrity.load_verified_authorization() "
            "may establish this, per-lead."
        ),
    }
    low = text.lower()
    for claim, why in FALSE_CLAIMS.items():
        if claim.lower() in low:
            raise IntegrityViolation(f"Unsubstantiated claim {claim!r} in client-facing text. {why}")


# ─── Model guard (defect D1 / Task 2.1) ───────────────────────────────────────
# SEB_MODEL_GUARD.md states the rule in prose and nothing implements it. This is
# the machine-enforced version: it HOLDS AND ALERTS (raises) rather than letting
# a security-critical task silently degrade onto a weak model.

#: Acceptable models, primary → last resort. Order is the fallback order.
MODEL_FALLBACK_CHAIN: tuple[str, ...] = (
    "nvidia/nemotron-3-ultra-550b-a55b",
    "nvidia/nemotron-3-super-120b-a12b",
    "openrouter/gpt-oss-20b:free",
    "step-3.7-flash:free",
    "tencent/hy3:free",  # LAST RESORT — non-security-critical tasks only.
)

#: The last tier is never acceptable for security-critical work.
LAST_RESORT_MODEL: str = MODEL_FALLBACK_CHAIN[-1]

#: Substrings that identify the forbidden primary, per SEB_MODEL_GUARD.md.
FORBIDDEN_FOR_SECURITY_CRITICAL: tuple[str, ...] = ("tencent/hy3", "hy3:free")

#: Task kinds SEB_MODEL_GUARD.md names as security-critical, plus the generic labels.
SECURITY_CRITICAL_TASKS: frozenset[str] = frozenset({
    "security-critical", "critical",
    "lead-gen", "risk-score", "retainer", "oss-pr", "msp",
})


def _norm(value: str) -> str:
    return value.strip().lower()


def _chain_index(model: str) -> Optional[int]:
    """Return the model's tier in MODEL_FALLBACK_CHAIN, tolerating id variants.

    'nvidia/nemotron-3-ultra' and 'nvidia/nemotron-3-ultra-550b-a55b' are the
    same tier; a provider prefix or a size suffix must not defeat the guard.
    """
    m = _norm(model)
    m_stem = m.split("/")[-1].split(":")[0]
    for i, entry in enumerate(MODEL_FALLBACK_CHAIN):
        e = _norm(entry)
        if m == e:
            return i
        e_stem = e.split("/")[-1].split(":")[0]
        if e_stem and (e_stem in m or (m_stem and m_stem in e_stem)):
            return i
    return None


def assert_model_acceptable(model: str, task_criticality: str = "security-critical") -> None:
    """Refuse to run a security-critical task on a forbidden or unvetted model.

    Implements SEB_MODEL_GUARD.md as an executable invariant. Raises
    IntegrityViolation instead of degrading; the caller must hold and alert.

    Non-security-critical tasks may use any tier, including the last resort.
    """
    if not isinstance(model, str) or not model.strip():
        raise IntegrityViolation(
            "MODEL GUARD: empty/invalid model identifier. A security-critical task "
            "may not run on an unidentified model."
        )

    if _norm(task_criticality) not in SECURITY_CRITICAL_TASKS:
        return  # Non-critical: the whole chain, last resort included, is permitted.

    m = _norm(model)
    chain = " → ".join(MODEL_FALLBACK_CHAIN)

    for bad in FORBIDDEN_FOR_SECURITY_CRITICAL:
        if bad in m:
            raise IntegrityViolation(
                f"MODEL GUARD: {model!r} is FORBIDDEN as primary for security-critical "
                f"task {task_criticality!r} (SEB_MODEL_GUARD.md). HOLD AND ALERT — do not "
                f"degrade and emit low-quality security work. Acceptable chain: {chain}"
            )

    idx = _chain_index(model)
    if idx is None:
        raise IntegrityViolation(
            f"MODEL GUARD: {model!r} is not on the vetted fallback chain and may not run "
            f"security-critical task {task_criticality!r}. Acceptable chain: {chain}"
        )
    if idx == len(MODEL_FALLBACK_CHAIN) - 1:
        raise IntegrityViolation(
            f"MODEL GUARD: {model!r} is the LAST RESORT tier ({LAST_RESORT_MODEL}) and is "
            f"permitted only for non-security-critical tasks, not {task_criticality!r}. "
            f"HOLD AND ALERT. Acceptable chain: {chain}"
        )
