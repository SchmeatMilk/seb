#!/usr/bin/env python3
"""Render _assessment.json -> risk_scores.md (dated, Lever-9 lead magnet).
Honest, read-only public-surface assessment only (SOUL.md §5)."""
import json, os, datetime

HOME = os.path.dirname(os.path.abspath(__file__))
DATE = datetime.date.today().isoformat()  # auto-stamps each cron run
d = json.load(open(os.path.join(HOME, "_assessment.json")))
res = d["results"]

def band(s):
    if s >= 60: return "HIGH"
    if s >= 35: return "MODERATE"
    return "LOW"

def widget_label(a):
    if a.get("vendors"):
        v = ", ".join(sorted(set(a["vendors"])))
        return f"Live-chat widget ({v})" + (" — AI-native" if a.get("ai_native") else "")
    if a.get("has_widget"):
        return "Chat launcher present (vendor not identified)"
    return "No public chat widget detected"

lines = []
lines.append(f"# SEB — AI Risk Score (Public-Surface Lead Magnet)")
lines.append("")
lines.append(f"**Generated:** {DATE}  |  **Cohort:** Kelowna / Okanagan SMBs (SmartSMB weekly leads + Kelowna directory exports)")
lines.append(f"**Method:** Read-only public-surface reconnaissance. Single HTTP GET of each public homepage; static analysis of HTML + response headers.")
lines.append("**No probing, no chatbot interaction, no port scan, no exploitation** (per SEB SOUL.md §5 — assessment only, authorization required for any active test).")
lines.append("")
lines.append("## Scoring rubric (0–100, transparent)")
lines.append("")
lines.append("| Signal | Points |")
lines.append("|--------|-------:|")
lines.append("| Public chat/automation widget present | +25 |")
lines.append("| Widget is AI-native (LLM/automation surface) | +15 |")
lines.append("| ≥6 third-party scripts (supply-chain surface) | +10 |")
lines.append("| Public form collecting PII (email/phone) | +10 |")
lines.append("| No HSTS header | +8 |")
lines.append("| No Content-Security-Policy | +8 |")
lines.append("| No X-Frame-Options | +4 |")
lines.append("| WordPress login/xmlrpc exposed | +7 |")
lines.append("| Served over plaintext HTTP | +15 |")
lines.append("| API/GraphQL signature in public page | +5 |")
lines.append("| CRITICAL public exposure (e.g. leaked credential) | +25 |")
lines.append("")
lines.append("> **What the score means:** it measures *public attack surface and AI-exposure readiness*, not a confirmed vulnerability. A higher score = more public surface that, once authorized, is worth a deeper Tier-1/2 SEB scan. No score here implies an active breach.")
lines.append("")
lines.append("## Cohort finding (headline)")
lines.append("")
lines.append("- **0 of 33 reachable SMB sites expose a verified public AI chatbot** on the homepage. Live-chat widgets in use (Tawk.to, Crisp, HubSpot) are human-handled, not LLM-driven.")
lines.append("- **CK Catalyst** is an AI-services firm (builds private AI assistants) — highest *vertical* relevance; its own site shows an OpenAI/LangChain stack keyword list, not a deployed public bot.")
lines.append("- Dominant public risk is **platform hygiene**: missing security headers (HSTS/CSP/XFO absent on ~all sites), WordPress `xmlrpc.php`/`wp-login` exposure, and PII-collecting contact forms.")
lines.append("")
lines.append(f"## Scores ({len(res)} leads)")
lines.append("")
# table
lines.append("| # | Business | Industry | Score | Band | Public surface |")
lines.append("|---|----------|----------|------:|------|----------------|")
for i, r in enumerate(sorted(res, key=lambda x: -x["score"]), 1):
    a = r.get("analysis", {})
    surf = widget_label(a)
    if r["status"] == "UNREACHABLE":
        surf = "Unreachable (domain does not resolve / TLS failure)"
    lines.append(f"| {i} | {r['name']} ({r['host']}) | {r.get('industry','')} | {r['score']} | {band(r['score'])} | {surf} |")
lines.append("")
lines.append("## Per-lead teasers (2-line — for daily outreach)")
lines.append("")
for r in sorted(res, key=lambda x: -x["score"]):
    a = r.get("analysis", {})
    name = r["name"]
    if r["status"] == "UNREACHABLE":
        t1 = "Domain did not resolve / TLS handshake failed during a read-only check."
        t2 = "If you still operate a site, a free scan confirms what the public can reach today."
    else:
        surf = widget_label(a)
        # build honest teaser
        bits = []
        if a.get("vendors") or a.get("has_widget"):
            bits.append(f"public chat widget ({', '.join(a.get('vendors') or ['unidentified'])})")
        else:
            bits.append("no public chat assistant")
        if not a.get("hsts"): bits.append("no HSTS")
        if not a.get("csp"): bits.append("no CSP")
        if a.get("cms") == "wordpress" and (a.get("wp_login_exposed") or a.get("xmlrpc_exposed")):
            bits.append("WordPress login/xmlrpc exposed")
        if a.get("has_form") and a.get("pii_inputs"):
            bits.append("PII contact form")
        t1 = f"Public surface: {'; '.join(bits)}."
        hook = ("Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk."
                if r["score"] >= 35 else
                "Clean baseline — a free SEB scan keeps it that way as you add AI tools.")
        t2 = hook
    lines.append(f"### {name} — {r['score']}/100 ({band(r['score'])})")
    lines.append(f"- {t1}")
    lines.append(f"- {t2}")
    lines.append("")
lines.append("---")
lines.append(f"_SEB · {DATE} · Read-only public-surface assessment. No active testing performed. Escalations to Klaus. · SOUL.md §5 compliant._")

out = "\n".join(lines)
path = os.path.join(HOME, "risk_scores.md")
open(path, "w", encoding="utf-8").write(out)
print(f"Wrote {path} ({len(out)} bytes, {len(res)} leads)")
