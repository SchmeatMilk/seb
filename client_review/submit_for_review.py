"""SEB — submit a client-facing asset for Brok/Malik sign-off (SOUL.md §4b).

Usage:
  python submit_for_review.py <asset_name> <draft_path> [--kind page|email|post|doc|report]

Writes <asset_name>_DRAFT.md (copy of draft_path) into client_review/ and appends a
`pending` entry to signoff_queue.jsonl. Never publishes. Safe to run any time.
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import time

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(HERE, "signoff_queue.jsonl")


def submit(asset: str, draft_path: str, kind: str) -> dict:
    if not os.path.isfile(draft_path):
        raise SystemExit(f"draft not found: {draft_path}")
    dest = os.path.join(HERE, f"{asset}_DRAFT.md")
    shutil.copyfile(draft_path, dest)
    rec = {
        "ts": time.time(),
        "asset": asset,
        "kind": kind,
        "draft_file": os.path.basename(dest),
        "status": "pending",
        "reviewer": None,
        "note": None,
    }
    with open(QUEUE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("asset")
    ap.add_argument("draft_path")
    ap.add_argument("--kind", default="doc")
    a = ap.parse_args()
    r = submit(a.asset, a.draft_path, a.kind)
    print("SUBMITTED FOR REVIEW (pending Brok/Malik sign-off):")
    print(json.dumps(r, indent=2))
