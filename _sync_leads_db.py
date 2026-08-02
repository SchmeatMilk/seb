#!/usr/bin/env python3
"""Sync _leads_manifest.json into the CRM `leads` table as status='identified',
authorization_given=0. Read-only lead-gen step. NEVER marks a lead authorized
or contacted. Idempotent on (company,url)."""
import json, os, sqlite3
from datetime import datetime, timezone

HOME = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HOME, "_leads_manifest.json")
DB = os.path.expanduser("~/src/seb/clients.db")

with open(MANIFEST, encoding="utf-8") as fh:
    data = json.load(fh)

# Filter out non-business share/OAuth URLs (google maps, linkedin/twitter share, OAuth)
SKIP_HOSTS = ("accounts.google.com", "maps.google.ca", "linkedin.com",
              "twitter.com", "facebook.com", "x.com")
leads = [l for l in data["leads"] if l["host"] not in SKIP_HOSTS]

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
existing = {(r["company"], r["url"]) for r in conn.execute("SELECT company,url FROM leads")}
inserted = 0
for l in leads:
    company = l.get("name") or l.get("host") or "unknown"
    key = (company, l["url"])
    if key in existing:
        continue
    conn.execute(
        """INSERT INTO leads (id, company, url, status, authorization_given, notes, created_at)
           VALUES (?,?,?,?,?,?,?)""",
        (f"ld_{abs(hash(key))%10**12:012d}", company, l["url"],
         "identified", 0, f"source={l['source']}; industry={l.get('industry','')}; city={l.get('city','')}",
         datetime.now(timezone.utc).isoformat()),
    )
    inserted += 1
conn.commit()
total = conn.execute("SELECT COUNT(*) n FROM leads").fetchone()["n"]
auth = conn.execute("SELECT COUNT(*) n FROM leads WHERE authorization_given=1").fetchone()["n"]
conn.close()
print(f"Inserted {inserted} new identified leads. Total leads: {total} | authorized: {auth}")
