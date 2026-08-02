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
