#!/usr/bin/env python3
"""SEB Lever-9 lead magnet: gather SmartSMB/Kelowna leads into a deduped manifest.
Read-only. No probing of targets. Collects public website URLs only.
"""
import csv, os, glob, json, re
from urllib.parse import urlparse

HOME = os.path.dirname(os.path.abspath(__file__))
WEEKLY = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")),
                      "OneDrive", "Documents", "Obsidian Vault", "SmartSMB", "Weekly_Leads")
LEADGEN = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Documents", "lead_gen", "output")
B2B = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "b2b_sniper_output.csv")

sources = []
# weekly leads (OneDrive SmartSMB)
sources += sorted(glob.glob(os.path.join(WEEKLY, "*.csv")))
# smartsmb dated exports (lead_gen output)
sources += sorted(glob.glob(os.path.join(LEADGEN, "smartsmb_*.csv")))
# b2b sniper (Kelowna)
if os.path.exists(B2B):
    sources.append(B2B)

def clean(url):
    if not url:
        return ""
    u = url.strip().strip('"').strip()
    u = u.replace("&amp;", "&")
    if not u:
        return ""
    if not u.startswith("http"):
        if "." in u and " " not in u:
            u = "https://" + u
        else:
            return ""
    return u

def host(u):
    try:
        return urlparse(u).netloc.lower().replace("www.", "")
    except Exception:
        return ""

leads = {}  # domain -> record
for f in sources:
    try:
        with open(f, newline="", encoding="utf-8-sig", errors="replace") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                name = (row.get("name") or "").strip()
                url = clean(row.get("website") or "")
                if not url:
                    continue
                h = host(url)
                if not h or h == "kelowna.biz" or h.endswith("kelowna.biz"):
                    continue
                # placeholder phone detection -> still keep, but flag
                phone = (row.get("phone") or "").strip()
                city = (row.get("city") or row.get("region") or "").strip()
                industry = (row.get("industry") or row.get("category") or row.get("cat_slug") or "").strip()
                rec = leads.get(h)
                if rec is None:
                    leads[h] = {
                        "name": name, "url": url, "host": h,
                        "phone": phone, "city": city, "industry": industry,
                        "source": os.path.basename(f),
                    }
                else:
                    # enrich missing fields
                    for k in ("phone", "city", "industry"):
                        if not rec.get(k) and locals()[k]:
                            rec[k] = locals()[k]
    except Exception as e:
        print("ERR reading", f, e)

out = {"generated": "2026-07-13", "count": len(leads), "leads": list(leads.values())}
with open(os.path.join(HOME, "_leads_manifest.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2)
print(f"Collected {len(leads)} unique lead domains from {len(sources)} source files.")
for d in sorted(leads):
    print(f"  {leads[d]['host']:35s} {leads[d]['name'][:28]:28s} {leads[d]['industry'][:20]}")
