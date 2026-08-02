#!/usr/bin/env python3
"""SEB Threat Intelligence Pipeline.

Monitors the L1B3RT4S and CL4R1T4S corpora for newly discovered attack classes.
The heavy lifting is performed by intel/corpus_inventory.py (dynamic import).
When new classes are found they are escalated via notify.escalate and a structured
entry is appended to ESCALATIONS.log.

SOUL.md §5 compliant: read-only assessment only — NO active probing/scanning of targets.
Intended to run daily via a Hermes cron job.
"""

import argparse
import datetime
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Set

HOME: Path = Path(__file__).resolve().parent

# --- Optional imports -------------------------------------------------------
try:
    from notify import escalate  # type: ignore
except Exception:  # pragma: no cover
    def escalate(event: str, message: str, *, meta: Any = None, require_approval: Any = None):
        print(f"[LOCAL ESCALATION] {event}: {message}", file=sys.stderr)
        return {"status": "queued_local", "event": event, "message": message}

# Load corpus_inventory.main via dynamic import (intel has no __init__)
INV_PATH: Path = HOME / "intel" / "corpus_inventory.py"
INVENTORY_MAIN = None
if INV_PATH.is_file():
    try:
        spec = importlib.util.spec_from_file_location("corpus_inventory", str(INV_PATH))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        INVENTORY_MAIN = getattr(mod, "main", None)
    except Exception as exc:  # pragma: no cover
        print(f"WARNING: failed to load corpus_inventory: {exc}", file=sys.stderr)
        INVENTORY_MAIN = None
else:  # pragma: no cover
    print("WARNING: corpus_inventory.py not found.", file=sys.stderr)

MODEL_GUARD_PATH = HOME / "SEB_MODEL_GUARD.md"


def check_model_guard() -> bool:
    """Return True if the SEB model-guard doc exists (strong model wired)."""
    return MODEL_GUARD_PATH.is_file()


ESCALATION_LOG_PATH: Path = HOME / "ESCALATIONS.log"


def log_escalation(event: str, message: str) -> None:
    ts = (
        datetime.datetime.now(datetime.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    entry = f"{ts}  [{event}]  {message}\n"
    try:
        ESCALATION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(ESCALATION_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(entry)
    except Exception as exc:  # pragma: no cover
        print(f"ERROR writing to ESCALATIONS.log: {exc}", file=sys.stderr)


def load_state(state_path: Path) -> Dict[str, Any]:
    if not state_path.is_file():
        return {}
    try:
        with open(state_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_state(state_path: Path, data: Dict[str, Any]) -> None:
    with open(state_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="SEB Threat Intelligence Pipeline")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.getcwd(),
        help="Directory for the state JSON file (default: CWD)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed output",
    )
    ns = parser.parse_args()

    output_dir = Path(ns.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    state_path = output_dir / "pipeline_intel_state.json"
    state = load_state(state_path)
    last_run_ts = state.get("last_run_timestamp")

    # Load previous corpus manifest
    manifest_path = HOME / "intel" / "corpus_manifest.json"
    prev_manifest = None
    if manifest_path.is_file():
        try:
            with open(manifest_path, "r", encoding="utf-8") as fh:
                prev_manifest = json.load(fh)
        except Exception as exc:  # pragma: no cover
            print(f"WARNING: failed to load corpus manifest: {exc}", file=sys.stderr)

    prev_classes: Set[str] = set()
    if prev_manifest and "l1b3rt4s" in prev_manifest:
        try:
            prev_classes = set(prev_manifest["l1b3rt4s"].get("attack_classes", []))
        except Exception:
            prev_classes = set()

    # Model guard
    if not check_model_guard():
        msg = "SEB held: strong model unavailable, refusing to run security task on weak model."
        escalate("model_guard_fail", msg)
        log_escalation("model_guard_fail", msg)
        print(f"[MODEL GUARD FAILED] {msg}")
        sys.exit(1)

    if INVENTORY_MAIN is None:
        print("ERROR: could not load corpus inventory. Aborting.", file=sys.stderr)
        sys.exit(1)

    # Run inventory to refresh + read latest manifest
    try:
        INVENTORY_MAIN()
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: corpus inventory raised: {exc}", file=sys.stderr)
        sys.exit(1)

    # Re-read the freshly written manifest for current classes
    current_manifest = None
    if manifest_path.is_file():
        try:
            with open(manifest_path, "r", encoding="utf-8") as fh:
                current_manifest = json.load(fh)
        except Exception:
            current_manifest = None

    cur_classes: Set[str] = set()
    if current_manifest and "l1b3rt4s" in current_manifest:
        cur_classes = set(current_manifest["l1b3rt4s"].get("attack_classes", []))

    new_classes = cur_classes - prev_classes

    summary_lines: list = []
    summary_lines.append("=== SEB Threat Intelligence Report ===")
    summary_lines.append(
        f"Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')}"
    )
    summary_lines.append(f"Last run: {last_run_ts or 'Never'}")

    if new_classes:
        msg = f"New attack classes discovered: {', '.join(sorted(new_classes))}"
        try:
            escalate("new_attack_class", msg, meta={"new_classes": sorted(new_classes)})
        except Exception:
            pass
        log_escalation("new_attack_class", msg)
        summary_lines.append(f"NEW ATTACK CLASSES: {msg}")
    else:
        summary_lines.append("No new attack classes discovered.")

    print("\n".join(summary_lines), flush=True)

    # Persist state
    state["last_run_timestamp"] = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()
    save_state(state_path, state)

    sys.exit(0)


if __name__ == "__main__":
    main()
