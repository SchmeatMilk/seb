"""
SEB Safety Kernel guard.

Pre-commit / self-modification hook: refuse any change to a protected path
unless it is human-authored. This is the structural enforcement of the six
immutable invariants (SEB_V2_MASTER_PLAN.md Phase 5). It is itself part of the
kernel and must never be weakened by an agent.

Usage (in a hook or self-mod pipeline):
    from safety_kernel.kernel_guard import check_changeset
    check_changeset(changed_files, author_is_human=False)  # raises KernelViolation
"""
from __future__ import annotations

import json
import os
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PROTECTED = json.loads((_HERE / "protected_paths.json").read_text(encoding="utf-8"))


class KernelViolation(Exception):
    """Raised when a non-human change touches a protected safety-kernel path."""


def _is_protected(rel_path: str) -> bool:
    rel = rel_path.replace("\\", "/")
    for p in _PROTECTED.get("protected_paths", []):
        p = p.rstrip("/")
        if rel == p or rel.startswith(p + "/") or rel.endswith("/" + p) or ("/" + p + "/") in rel:
            return True
    low = rel.lower()
    for sub in _PROTECTED.get("protected_substrings", []):
        if sub.lower() in low:
            return True
    return False


def check_changeset(changed_files: list[str], *, author_is_human: bool = False) -> None:
    """Refuse the changeset if any protected path is touched by a non-human.

    `changed_files` are repo-relative paths (e.g. "integrity.py",
    "safety_kernel/KERNEL.md"). `author_is_human` is set True only when a human
    has explicitly signed off — never by an agent.
    """
    hits = [f for f in changed_files if _is_protected(f)]
    if not hits:
        return
    if author_is_human:
        # Human-authored changes to the kernel are permitted but must be explicit.
        return
    raise KernelViolation(
        "SAFETY KERNEL: non-human change to protected path(s): "
        + ", ".join(hits)
        + ". These may only be modified by Malik. Refusing."
    )


if __name__ == "__main__":
    # Quick self-test when run directly.
    try:
        check_changeset(["integrity.py"], author_is_human=False)
        print("FAIL: should have raised")
    except KernelViolation as e:
        print("OK guard holds:", e)
    check_changeset(["gauntlet.py"], author_is_human=False)
    print("OK non-kernel change permitted")
