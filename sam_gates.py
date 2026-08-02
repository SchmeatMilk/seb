"""
SEB/Sam — outreach gates.

Hard rule: Sam never sends without Malik's explicit release. Both gates default
CLOSED and fail closed on any error, including a missing or malformed state file.
Neither gate implies the other. Only Malik may open them; no agent may write this file.

Task 3.2 (SEB_V2_MASTER_PLAN.md P3). Copied verbatim from the plan; this is the
machine-enforced brake that must hold before Sam sends any external message.
"""
from __future__ import annotations
import json, os

GATE_FILE = os.path.join(os.path.dirname(__file__), "sam_gates.json")


class GateClosed(Exception):
    """Raised when an action requires a gate that Malik has not opened."""


def _gates() -> dict:
    try:
        with open(GATE_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}                      # fail closed


def assert_may_send_without_review() -> None:
    """Gate A. Until Malik opens this, every message goes to the review queue."""
    if _gates().get("gate_a_autonomous_send") is not True:
        raise GateClosed(
            "GATE A CLOSED: Sam may draft into client_review/ but may not send. "
            "Only Malik opens this."
        )


def signature_block() -> str:
    """Gate B. Until Malik opens this, all outreach signs as Malik."""
    if _gates().get("gate_b_sam_signs_own_name") is True:
        return "Sam\nSEB — Security Inquisitor Balance"
    return "Malik\nSEB — Security Inquisitor Balance"
