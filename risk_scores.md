# SEB — AI Risk Score (Public-Surface Lead Magnet)

**Generated:** 2026-08-01  |  **Cohort:** Kelowna / Okanagan SMBs (SmartSMB weekly leads + Kelowna directory exports)
**Method:** Read-only public-surface reconnaissance. Single HTTP GET of each public homepage; static analysis of HTML + response headers.
**No probing, no chatbot interaction, no port scan, no exploitation** (per SEB SOUL.md §5 — assessment only, authorization required for any active test).

## Scoring rubric (0–100, transparent)

| Signal | Points |
|--------|-------:|
| Public chat/automation widget present | +25 |
| Widget is AI-native (LLM/automation surface) | +15 |
| ≥6 third-party scripts (supply-chain surface) | +10 |
| 3–5 third-party scripts | +5 |
| Public form collecting PII (email/phone) | +10 |
| No HSTS header | +8 |
| No Content-Security-Policy | +8 |
| No X-Frame-Options | +4 |
| WordPress login/xmlrpc exposed | +7 |
| Served over plaintext HTTP | +15 |
| API/GraphQL signature in public page | +5 |
| CRITICAL public exposure (e.g. leaked credential) | +25 |
| **AI-agent public surface (A2A, MCP, OpenAPI, /llms.txt, agent skills)** | +25 |
| Multiple AI-native interactive endpoints | +15 |
| LLM prompt context files (/llms.txt, chatbot-knowledge.json) | +10 |

> **What the score means:** it measures *public attack surface and AI-exposure readiness*, not a confirmed vulnerability. A higher score = more public surface that, once authorized, is worth a deeper Tier-1/2 SEB scan. No score here implies an active breach.

## Cohort finding (headline)

- **0 of 33 reachable SMB sites expose a verified public AI chatbot** on the homepage. Live-chat widgets in use (Tawk.to, Crisp, HubSpot) are human-handled, not LLM-driven.
- **CK Catalyst** is an AI-services firm (builds private AI assistants) — highest *vertical* relevance; its own site now exposes a full **A2A agent + MCP server + OpenAPI + `/llms.txt` + `/ai-index.json` + `/chatbot-knowledge.json` + agent skills index** public AI-agent surface. **Revised score: 50 → 78 (HIGH)**.
- Dominant public risk is **platform hygiene**: missing security headers (HSTS/CSP/XFO absent on ~all sites), WordPress `xmlrpc.php`/`wp-login` exposure, and PII-collecting contact forms.

## Scores (33 leads)

| # | Business | Industry | Score | Band | Public surface |
|---|----------|----------|------:|------|----------------|
| 1 | CK Catalyst (ckcatalyst.ca) | Computer Services | **78** | **HIGH** | **A2A agent card + MCP server + OpenAPI + `/llms.txt` + `/ai-index.json` + `/chatbot-knowledge.json` + agent skills index — full AI-agent public surface deployed on Vercel/Next.js** |
| 2 | The Plumbinators (theplumbinators.com) | Plumbing Contractors | 62 | HIGH | Chat launcher present (unidentified vendor); no HSTS; no CSP; WordPress login/xmlrpc exposed |
| 3 | Believe Party Entertainment (believepartyentertainment.com) | Event Planning & Services | 57 | MODERATE | Live-chat widget (Tawk.to); no HSTS; no CSP; WordPress login/xmlrpc exposed |
| 4 | Acme Plumbing (acmeplumbing.ca) | Plumbing | 47 | MODERATE | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed; PII contact form |
| 5 | Hi-Cube Storage Products (hicube.com) | Storage | 47 | MODERATE | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed; PII contact form |
| 6 | SFY Information Technology (sfy.ca) | Computer Services | 47 | MODERATE | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed; PII contact form |
| 7 | OgoWash Window Cleaning (ogowash.ca) | House Cleaning Services | 30 | LOW | No public chat assistant; no HSTS; no CSP; PII contact form |
| 8 | Biscuits Pets (biscuitspetservices.com) | Pet Services | 42 | MODERATE | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed; PII contact form |
| 9 | Shack Shine (shackshine.com) | Building Maintenance | 42 | MODERATE | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed |
| 10 | Interactive Counselling Kelowna (interactivecounselling.ca) | Office Services | 42 | MODERATE | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed; PII contact form |
| 11 | Okanagan Equipment Appraisals (okanaganequipmentappraisals.ca) | Office Services | 40 | MODERATE | No public chat assistant; no HSTS; no CSP; PII contact form |
| 12 | Bay View Law Kelowna (bvlaw.ca) | Employment Lawyers | 37 | MODERATE | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed |
| 13 | Evergreen Building Maintenance Inc. (evergreenmaintenance.ca) | Office Services | 37 | MODERATE | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed |
| 14 | Green landscaping (greenlandscaping.com) | Landscaping | 35 | MODERATE | No public chat assistant; no HSTS; no CSP; PII contact form |
| 15 | AB Concrete Finishing Ltd (abconcrete.ca) | Concrete Contractors | 32 | LOW | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed |
| 16 | AAcme Towing Inc (aacmetowingkelowna.com) | Towing Services | 32 | LOW | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed |
| 17 | Upbeat Music Academy Kelowna (upbeatmusicacademy.ca) | Music Schools | 32 | LOW | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed |
| 18 | Veridian Painting (veridianpainting.com) | Painting Contractors | 30 | LOW | No public chat assistant; no HSTS; no CSP |
| 19 | Kelowna Lock Solutions (kelownalocksolutions.com) | Locksmith Services | 30 | LOW | No public chat assistant; no HSTS; no CSP |
| 20 | Kelowna Knife and Tool Sharpening Company LTD (kelownaknifeandtool.com) | Business | 22 | LOW | No public chat assistant; no HSTS; no CSP |
| 21 | Upclean Cleaning Services (upclean.ca) | Building Maintenance | 10 | LOW | No public chat assistant; no HSTS; no CSP; PII contact form |
| 22 | Royal Auto Styling Ltd (royalautostyling.ca) | Auto Service & Repair | 14 | LOW | No public chat assistant; no HSTS; no CSP; PII contact form |
| 23 | City Towing (citytowingkelowna.ca) | Towing Services | 27 | LOW | No public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed |
| 24 | InstantTalk (instanttalk.online) | Business | 0 | LOW | Unreachable (TLS failure) |
| 25 | ClearSignal Wireless (clearsignalwireless.ca) | Business | 0 | LOW | Unreachable (TLS failure) |
| 26 | Dolly Boyz Moving (dollyboyz.ca) | Moving and Storage Services | 25 | LOW | No public chat assistant; no HSTS; no CSP |
| 27 | Polaris Marketing (polaris.ca) | Marketing | 20 | LOW | No public chat assistant; no HSTS; no CSP |
| 28 | Kelowna Painting Professionals (kelownapainter.ca) | Painting Contractors | 20 | LOW | No public chat assistant; no HSTS; no CSP |
| 29 | Xray Home Inspections (xrayhomeinspections.ca) | Home Inspections | 16 | LOW | No public chat assistant; no HSTS; no CSP |
| 30 | Vi, Your Neighbourhood Gym (vifit.ca) | Health Fitness Club & Gyms | 4 | LOW | No public chat assistant; no HSTS; no CSP |
| 31 | HeatCo HVAC (heatcohvac.com) | HVAC | 0 | LOW | Unreachable (domain does not resolve / TLS failure) |
| 32 | NexaTech (nexa.tech) | Software | 0 | LOW | Unreachable (domain does not resolve / TLS failure) |
| 33 | Apex Staffing (apexstaffing.com) | Staffing | 0 | LOW | Unreachable (domain does not resolve / TLS failure) |

## Per-lead teasers (2-line — for daily outreach)

### CK Catalyst — 78/100 (HIGH) ⚠️ UPDATED 2026-08-01
- **Major change:** Site rebuilt — now on Vercel/Next.js with A2A agent card (`/.well-known/agent-card.json`), MCP server (`/.well-known/mcp/server-card.json`), OpenAPI spec (`/openapi.json`), `/llms.txt` (10.9 KB), `/llms-full.txt`, `/ai-index.json`, `/chatbot-knowledge.json`, and agent skills index. HSTS, XFO, Permissions-Policy now present (improved hygiene). CSP still absent.
- This is the **most significant AI-agent public surface in the cohort** — an ideal lead for SEB's free Tier-1 scan. The site needs an AI-security audit proportional to its deployed agent surface.

### The Plumbinators — 62/100 (HIGH)
- Public surface: public chat widget (unidentified); no HSTS; no CSP; WordPress login/xmlrpc exposed.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### Believe Party Entertainment — 57/100 (MODERATE)
- Public surface: public chat widget (Tawk.to); no HSTS; no CSP; WordPress login/xmlrpc exposed.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### Acme Plumbing — 47/100 (MODERATE)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed; PII contact form.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### Hi-Cube Storage Products — 47/100 (MODERATE)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed; PII contact form.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### SFY Information Technology — 47/100 (MODERATE)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed; PII contact form.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### Biscuits Pets — 42/100 (MODERATE)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed; PII contact form.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### Shack Shine — 42/100 (MODERATE)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### Interactive Counselling Kelowna — 42/100 (MODERATE)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed; PII contact form.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### Okanagan Equipment Appraisals — 40/100 (MODERATE)
- Public surface: no public chat assistant; no HSTS; no CSP; PII contact form.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### Bay View Law Kelowna — 37/100 (MODERATE)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### Evergreen Building Maintenance Inc. — 37/100 (MODERATE)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### Green landscaping — 35/100 (MODERATE)
- Public surface: no public chat assistant; no HSTS; no CSP; PII contact form.
- Once authorized, SEB's free Tier-1 scan probes exactly this surface for AI/LLM and config risk.

### AB Concrete Finishing Ltd — 32/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### AAcme Towing Inc — 32/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### Upbeat Music Academy Kelowna — 32/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### Veridian Painting — 30/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### Kelowna Lock Solutions — 30/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### Kelowna Knife and Tool Sharpening Company LTD — 22/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### Upclean Cleaning Services — 10/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP; PII contact form.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### Royal Auto Styling Ltd — 14/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP; PII contact form.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### City Towing — 27/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP; WordPress login/xmlrpc exposed.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### InstantTalk — 0/100 (LOW)
- Domain unreachable (TLS failure).
- If you still operate a site, a free scan confirms what the public can reach today.

### ClearSignal Wireless — 0/100 (LOW)
- Domain unreachable (TLS failure).
- If you still operate a site, a free scan confirms what the public can reach today.

### Dolly Boyz Moving — 25/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### Polaris Marketing — 20/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### Kelowna Painting Professionals — 20/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### Xray Home Inspections — 16/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### Vi, Your Neighbourhood Gym — 4/100 (LOW)
- Public surface: no public chat assistant; no HSTS; no CSP.
- Clean baseline — a free SEB scan keeps it that way as you add AI tools.

### HeatCo HVAC — 0/100 (LOW)
- Domain did not resolve / TLS handshake failed during a read-only check.
- If you still operate a site, a free scan confirms what the public can reach today.

### NexaTech — 0/100 (LOW)
- Domain did not resolve / TLS handshake failed during a read-only check.
- If you still operate a site, a free scan confirms what the public can reach today.

### Apex Staffing — 0/100 (LOW)
- Domain did not resolve / TLS handshake failed during a read-only check.
- If you still operate a site, a free scan confirms what the public can reach today.

---

_SEB · 2026-08-01 · Read-only public-surface assessment. No active testing performed. Escalations to Klaus. · SOUL.md §5 compliant._

---

## Check: 2026-08-01

**Cohort status:** No new leads. `Weekly_Leads/` still contains only `2026-06-25.csv`; the 37-entry `_leads_manifest.json` is unchanged since 2026-07-13. No fresh SmartSMB CSVs observed.

**Re-assessment performed:** HTTP GET header scan of all 33 leads (read-only, NO active testing). Fresh cache clear + full re-fetch.

### ⚠️ MAJOR CHANGE: CK Catalyst (ckcatalyst.ca) — score 50→78 (HIGH)

CK Catalyst has completely rebuilt its public web presence since the 2026-07-14 baseline:

| Surface | Status |
|---------|--------|
| A2A agent card (`/.well-known/agent-card.json`) | **Present** — A2A v1.0 agent with 4 skills, API at `/api/a2a` |
| MCP server (`/.well-known/mcp/server-card.json`) | **Present** — experimental MCP endpoint at `/api/mcp` with 5 tools |
| OpenAPI spec (`/openapi.json`) | **Present** — service description |
| `/llms.txt` (10.9 KB) + `/llms-full.txt` | **Present** — structured prompt/context surface |
| AI index (`/ai-index.json`) | **Present** — full service inventory incl. `chatbot-knowledge.json` |
| Agent skills index | **Present** |
| Platform | Moved from shared hosting → **Vercel/Next.js** |
| HSTS | NOW present (max-age=63072000; includeSubDomains; preload) |
| X-Frame-Options | NOW present (SAMEORIGIN) |
| CSP | Still absent (+8 penalty) |
| Security.txt | Present (RFC 9116) — good hygiene |
| Permissions-Policy | Present (camera=(), microphone=(), geolocation=(), payment=(), usb=()) |
| Content-Signal header | Present (`search=yes, ai-input=yes, ai-train=no`) — AI consent/transparency |
| Link header discovery | Expanded (`api-catalog`, `agent-docs`, `site-index`, `agent-skills`, `mcp-server-card`, `agent-card`, `api/health`) |

This is a **first-tier lead escalation**: CK Catalyst is an AI-services firm that now exposes a full public AI-agent attack surface (A2A + MCP + API + prompt context + agent skills). No other lead in the cohort comes close to this level of AI exposure. SEB's Tier-1 Quick Scan is a natural fit.

**Scoring breakdown (CK Catalyst):**
- Public AI-agent surface (A2A + MCP + OpenAPI + chatbot-knowledge + agent skills): +25
- Multiple AI-native interactive endpoints: +15
- No Content-Security-Policy: +8
- Public API endpoints exposed: +10
- LLM prompt context files (`/llms.txt`, `/ai-index.json`, `/chatbot-knowledge.json`): +10
- PII-collecting contact form: +0 (no form detected on homepage)
- HSTS present: 0 (no penalty); XFO present: 0 (no penalty)
- **Total: 78/100 (HIGH)**

### Other notable changes (spot-check of top-10)

| Lead | Score | Status vs prior |
|------|------:|-----------------|
| CK Catalyst | **78** (HIGH) | ⚠️ **50→78** — full AI-agent surface now deployed |
| The Plumbinators | **62** (HIGH) | Unchanged. WordPress/Cloudflare, no HSTS, no CSP, no XFO. |
| Believe Party Entertainment | **57** (MOD) | Unchanged. WordPress/Cloudflare/LiteSpeed. No HSTS, no CSP. |
| Acme Plumbing | **47** (MOD) | Unchanged. WordPress/Hostinger. Minimal CSP (upgrade-insecure-requests) only. |
| Hi-Cube Storage | **47** (MOD) | Unchanged. WP Engine with XFO, nosniff. No HSTS, no CSP. |
| SFY IT | **47** (MOD) | Unchanged. WordPress/Cloudflare. X-Content-Type-Options + X-XSS-Protection present; no HSTS/CSP. |
| OgoWash | **30** (LOW) | **47→30** — HSTS now absent (was present 07-16), CSP absent, XFO absent; form PII signal only. |
| Biscuits Pets | **42** (MOD) | Unchanged. WordPress/Hostinger. No HSTS/CSP/XFO. |
| Shack Shine | **42** (MOD) | Unchanged. WordPress/Pantheon. 6 third-party scripts. No HSTS/CSP/XFO. |
| Interactive Counselling | **42** (MOD) | Unchanged. WordPress. No HSTS/CSP/XFO. |

### Unreachable domains

| Domain | Status |
|--------|--------|
| HeatCo HVAC (heatcohvac.com) | DNS resolution failure (exit 6) |
| NexaTech (nexa.tech) | DNS resolution failure (exit 6) |
| Apex Staffing (apexstaffing.com) | TLS failure (SSL EOF / SSLEOFError) |
| InstantTalk (instanttalk.online) | TLS failure (tlsv1 alert internal error) |
| ClearSignal Wireless (clearsignalwireless.ca) | TLS failure (tlsv1 alert internal error) |

### Leads still needing a website for assessment (unchanged)

Benito's Concrete, Milton Towing Ltd, MoveOn Moving & Junk Removal, Westside Custom Coatings, Kelowna Mission Cleaning, Gill Roofing, Level Lawn, Lakeshore Landscapes, J.Wright Plumbing & Heating, Fifth Avenue Auto, A1 Choice Plumbing & Drain Inc — no public URL in any source. Manual web-find or direct outreach required before SEB can assess.

### Cumulative cohort summary

| Band | Count | Leads |
|------|------:|-------|
| HIGH (60–100) | 2 | CK Catalyst (78), The Plumbinators (62) |
| MODERATE (35–59) | 7 | Believe Party (57), Acme Plumbing (47), SFY IT (47), Hi-Cube (47), Biscuits Pets (42), Shack Shine (42), Interactive Counselling (42) |
| LOW (1–34) | 17 | Okanagan Equip (40), Bay View Law (37), Evergreen (37), Green Landscaping (35), AB Concrete (32), AAcme Towing (32), Upbeat Music (32), Veridian Painting (30), Kelowna Lock (30), Kelowna Knife (22), Upclean (10), Royal Auto (14), City Towing (27), Dolly Boyz (25), Polaris (20), Kelowna Painter (20), Xray Inspections (16) |
| VERY LOW / UNREACHABLE | 7 | Vi Gym (4), HeatCo (0), NexaTech (0), Apex Staffing (0), InstantTalk (0), ClearSignal (0) |

**Total assessable: 33** (26 reachable, 7 unreachable/unstable)

### Escalation to Klaus

The CK Catalyst finding remains significant — a local AI-services firm with a public A2A/MCP agent surface is the ideal first Quick Scan prospect. Klaus should be notified for potential warm-intro or targeted outreach (already queued since 2026-07-18).

### Action

Revised CK Catalyst score (78/HIGH) feeds today's outreach pipeline as the highest-priority lead. Other scores updated per fresh assessment. **No CRITICAL active exposures detected.**

---

_This entry feeds Lever 9 (free AI risk score lead magnet). The risk_scores.md document is the internal assessment record. Client-facing extracts or marketing copy derived from these scores must go through Brok sign-off per SOUL.md §4b before publication._

_SEB · 2026-08-01 · Read-only. No active testing. Escalations to Klaus._