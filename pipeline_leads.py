#!/usr/bin/env python3
"""SEB-SALES — Lead Generation Pipeline (Authorization-Only).

Generates individualized outreach drafts ONLY for prospects with signed
authorization on file (authorization_given=1 in CRM). Never contacts or
scans unauthorized targets. Writes drafts to client_review/ for Brok/Malik
sign-off before any send (SOUL.md §4b).

SOUL.md §5 hard gate: No outreach without signed authorization.
SOUL.md §4b hard gate: No client-facing material ships without Brok/Malik sign-off.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

HOME = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HOME, "clients.db")
REVIEW_DIR = os.path.join(HOME, "client_review")
AUTH_TEMPLATE_PATH = os.path.join(HOME, "AUTH_TEMPLATE.md")

# Permissible lead-gen channels (SOUL.md §5-compliant)
CHANNELS = {
    "cold_email": "Permission-first email invitation to opt-in intake only. No claims of prior testing, no scanning.",
    "linkedin_dm": "Invitation to intake — requires Klaus /post approval before send (SOUL.md §6).",
    "inbound_intake": "Auto-response on receipt of signed authorization_record_*.json. No human initiation.",
}

OUTREACH_TEMPLATE = """---
draft_for: {company}
generated: {timestamp}
status: draft_unsigned
---

# SEB — $500 Quick Scan: Opt-In Outreach ({company})

**Authorization status:** Signed authorization on file ✓

Hi {first_name} at {company},

Thank you for completing the SEB authorization intake. Your signed
authorization record is on file, and we can proceed with your
**$500 Quick Scan — OWASP LLM Top-10** audit.

Here's what happens next:

1. **We run our automated gauntlet** — 100+ probes across 4 tools,
   OWASP-mapped. Non-destructive, rate-limited. Takes ~2 hours.
2. **Human triage** — ~15 min review by SEB analyst.
3. **You receive a scored PDF report** with prioritized fixes, within
   5 business days.

No surprises. You approved the scope, we stay within it.

Reply to confirm you'd like to proceed, or let me know if you have
questions first.

— SEB (Security Inquisitor Balance)
malik@seb.security
"""


def get_authorized_leads(conn) -> list[dict]:
    """Fetch leads with signed authorization on file."""
    rows = conn.execute(
        "SELECT id, company, url, status, authorization_given, notes "
        "FROM leads WHERE authorization_given = 1 "
        "ORDER BY created_at DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def extract_first_name(company: str) -> str:
    """Best-effort first name extraction; falls back to 'there'."""
    name = (company or "").strip()
    if not name:
        return "there"
    # Try splitting on common delimiters
    for sep in [" ", "/", "-", ","]:
        parts = name.split(sep, 1)
        if len(parts) > 1 and len(parts[0]) > 1:
            return parts[0]
    return name.split()[0] if " " in name else "there"


def produce_draft(lead: dict) -> str:
    """Generate an individualized outreach draft for an authorized lead."""
    os.makedirs(REVIEW_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    draft = OUTREACH_TEMPLATE.format(
        company=lead["company"],
        timestamp=ts,
        first_name=extract_first_name(lead["company"]),
    )
    safe_name = lead["company"].replace(" ", "_").replace("/", "_").replace("\\", "_")[:40]
    filename = f"{safe_name}_outreach_DRAFT.md"
    path = os.path.join(REVIEW_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(draft)

    # Append to signoff queue
    queue_path = os.path.join(REVIEW_DIR, "signoff_queue.jsonl")
    entry = {
        "asset": filename,
        "company": lead["company"],
        "generated": ts,
        "status": "pending",
        "type": "outreach_draft",
    }
    with open(queue_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return path


def main():
    if not os.path.isfile(DB):
        print(f"ERROR: CRM database not found at {DB}")
        sys.exit(1)

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    authorized = get_authorized_leads(conn)
    identified = conn.execute(
        "SELECT COUNT(*) FROM leads WHERE status='identified'"
    ).fetchone()[0]

    print(f"=== SEB-SALES Pipeline Report ===")
    print(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    print(f"Total leads in CRM: {total}")
    print(f"  - Identified (unauthorized): {identified}")
    print(f"  - Authorized (signed): {len(authorized)}")

    if not authorized:
        print("\n⚠️  AUTH-GATED: 0 authorized prospects. No outreach drafts generated.")
        print("   All leads are status=identified, authorization_given=0.")
        print("   Pipeline blocked until a signed authorization form is received.")
    else:
        print(f"\n📋 Producing drafts for {len(authorized)} authorized prospects:")
        for lead in authorized:
            path = produce_draft(lead)
            print(f"   ✓ {lead['company']} -> {path}")

    # Check signoff queue
    queue_path = os.path.join(REVIEW_DIR, "signoff_queue.jsonl")
    pending_queue = 0
    if os.path.isfile(queue_path):
        with open(queue_path) as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if entry.get("status") == "pending":
                        pending_queue += 1

    print(f"\n📋 Signoff queue: {pending_queue} pending items (awaiting Brok/Malik)")
    print(f"\nPermissible channels (SOUL.md §5-compliant):")
    for ch, desc in CHANNELS.items():
        print(f"  - {ch}: {desc}")
    print(f"\nNOT permissible: contacting unauthorized targets, automated scanning,")
    print(f"  any engagement without signed authorization record on file.")

    conn.close()


if __name__ == "__main__":
    main()
