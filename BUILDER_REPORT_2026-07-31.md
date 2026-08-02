# SEB — Builder Report: Deep Research & System Audit

**Date:** 2026-07-31 (UTC)
**Prepared by:** Klaus (CEO/operational manager), via Hermes deep-research session
**For:** SEB-CORE (builder agent) — read this fully before any build work
**Status:** Research-complete. Gaps are severity-ranked; execute in priority order.

---

## 0. TL;DR — What the builder needs to know right now

1. **Your standards mappings are CORRECT and verified** (OWASP LLM 2025, OWASP Agentic 2026 ASI01–10, MITRE ATLAS 16/173). Do not redo them. The V3 "stale taxonomy" debt is resolved (commit `02ea5c7`).
2. **A whole new attack surface is live that you don't cover: OWASP MCP Top 10 (June 2026).** 30+ MCP CVEs were filed in Jan–Feb 2026 alone; Palo Alto Unit 42 measured 78.3% attack success across 5 MCP servers. Your flagship prospect (CK Catalyst) **already exposes a public MCP server**. This is your next differentiator — build it.
3. **Your heavy engines (garak 0.15.1, pyrit 0.14.0, giskard 2.19.2) are installed but never fire.** Every dogfood run skips them. You need a local HTTP test harness so they actually run.
4. **All 7 SEB cron jobs are pinned to `tencent/hy3` (nous)** — this violates your own SEB_MODEL_GUARD.md AND Malik's standing directive (global fallback chain). This is the #1 integrity fix.
5. **Your first deal (CK Catalyst, $500) has a delivered passive Quick Scan and a signed authorization on file — but the authorized ACTIVE phase hasn't run.** That's the fastest path to real revenue.
6. **Credibility gate decision is due now** (3-week PR-monitor window from STRATEGY.md expires ~Aug 4): 3 OSS PRs open (garak #1940, #1963; L1B3RT4S #86), zero merged.

---

## 1. Verified System State (2026-07-31, from live files/DB/crons)

### Codebase
- 7 git commits, all Jul 9–14; **working tree is 17 days ahead of git** (uncommitted: `email_compiler.py`, `email_templates/`, `msp_pitches.md`, `risk_scores.md`, `_assessment.json`, `_leads_manifest.json`, `_sync_leads_db.py`, etc.). Commit this work.
- Engines installed in `.venv`: **garak 0.15.1, pyrit 0.14.0, giskard 2.19.2**, reportlab 5.0.0, pystache 0.6.8, requests, python-dotenv.
- 12 pytest pass (tests isolated via tmp_path; DB/PDF never touch prod paths).
- Dogfood PDF exists: `output/seb_dogfood_self.pdf` (74 probes, 0 leaks — L1B3RT4S only).

### Databases (`clients.db`)
| Table | Rows | Notes |
|---|---|---|
| clients | 2 | 1 dogfood/active, 1 free/lead (CK Catalyst) |
| engagements | 2 | dogfood + CK Catalyst quick scan |
| findings | 0 | **no active-phase findings persisted yet** |
| leads | 33 | ALL status=identified, 0 authorized in leads table |
| invoices | 1 | dry-run placeholder |
| intel_log | **0** | **BUG: `log_intel()` exists in client_db but `pipeline_intel.py` never calls it** |

### Crons (7 SEB jobs, all live)
| Job | Schedule | Model | Issue |
|---|---|---|---|
| SEB daily intel | 06:00 | **tencent/hy3** | violates model guard |
| SEB daily leads | 09:30 | **tencent/hy3** | violates model guard |
| SEB risk-score | 09:30 | **tencent/hy3** | violates model guard |
| SEB weekly retainer | Mon 08:00 | **tencent/hy3** | violates model guard |
| SEB oss-pr | Mon 10:00 | **tencent/hy3** | violates model guard |
| SEB msp | Wed 14:00 | **tencent/hy3** | violates model guard |
| SEB daily digest → Malik | 20:00 | step-3.7-flash:free | OK (reporting, non-critical) |

All jobs run with `workdir C:\Users\mbapt\src\seb`. All last-status "ok".

### OSS PR status (checked live via gh CLI)
- **NVIDIA/garak #1940** — `docs: add OWASP LLM Top 10 mapping tutorial` — **OPEN** (2026-07-10)
- **NVIDIA/garak #1963** — `tests: validate plugin enumeration contract` — **OPEN** (2026-07-14); predecessor #1962 CLOSED (not merged)
- **elder-plinius/L1B3RT4S #86** — `tools: add defensive corpus validator` — **OPEN** (2026-07-10)
- **0 merged.** Credibility gate per STRATEGY.md Pillar 1: PR-merge monitor started 07-14; funded fallback trigger (cert ~$200) is **due ~Aug 4**.

### Delivery state
- Telegram: **live since 2026-07-21** (test ping verified). Escalation queue drained: 15/15 delivered.
- `ESCALATIONS.log` shows: CK Catalyst outreach APPROVED (07-22), quick-scan delivered (07-27), pipeline auth-gate working, lead-gen pivot recommended (Kelowna trades won't convert — 0/33 have AI chatbots).
- **CK Catalyst:** signed authorization on file (`authorizations/authorization_CK_Catalyst.json`, sig `f3a2b1c4`), passive Quick Scan delivered (MODERATE 45/100), invoice pending. **Active authorized phase NOT yet run.**

### Known doc conflicts (fix in this pass)
1. **Pricing:** Landing page (`$500 / $2,500 / $2,000/mo`) ≠ PRICING.md (`$500 / $500/mo / $2,000` — Malik-confirmed 07-12). **PRICING.md is canonical.** Landing page is stale (pre-dates the 07-12 decision).
2. **Model:** SEB_MODEL_GUARD.md pins `opencode-zen/big-pickle` + fallback chain; PROFITABILITY_PLAN says "all hy3/Nous"; actual crons pin hy3. All three must be reconciled to the fallback chain below.
3. **ATLAS count:** V3 brief said 84 techniques; live source = **173** (SEB code already corrected this — keep 173).

---

## 2. External Research (verified 2026-07-31)

### Market
- AI Red Teaming **Services**: $2.26B (2026) → **$6.17B (2030)**, 28.5% CAGR (The Business Research Company; Research and Markets: $1.75B 2025 → $2.26B 2026, 28.8% CAGR).
- AI Red Teaming **Solutions**: +$6.69B growth 2026–2030, 25.1% CAGR (Technavio).
- SEB's $500 lane still has **no direct managed competitor**. Nearest managed: ~$5K (AI Vyuh); boutique $12K+ (DSE). OSS tools (garak, PyRIT, promptfoo, DeepTeam) are DIY; commercial platforms (Mindgard, Lakera, HiddenLayer, Protect AI, CalypsoAI, Robust Intelligence, Adversa, TrojAI, Cranium) start well above SEB pricing.

### Standards — what's confirmed / what's new
| Framework | Status | SEB coverage |
|---|---|---|
| OWASP LLM Top 10 (2025) | Current | ✅ Correct (LLM01–LLM10 verified) |
| OWASP Agentic 2026 (ASI01–10) | Released 2025-12-09, 100+ experts | ✅ Correct names verified against official page + DeepTeam detail |
| **OWASP MCP Top 10** | **NEW — June 2026** | ❌ **Not covered — build it** |
| MITRE ATLAS | 16 tactics / **173 techniques** (matrix v2026.06) | ✅ Correct in code |
| NIST AI RMF + **AI 600-1** (GenAI profile, 12 named risks, July 2024) | Current | 🟡 Map findings to 600-1 in reports (cheap credibility win) |
| EU AI Act (AI Omnibus) | **Annex III high-risk → 2 Dec 2027; Annex I embedded → 2 Aug 2028** (Council agreement June 2026; provisional) | ✅ "Dec 2027" correct — add Aug 2028 nuance |
| HackerOne Good Faith AI Research Safe Harbor | **Live since 20 Jan 2026** (press release confirmed) | ✅ SEB framing current |
| ISO/IEC 42001 | Current | 🟡 Mention in compliance section |

### OWASP MCP Top 10 — why it matters (the new differentiator)
- OWASP published an **MCP Top 10 in June 2026** (10 risk categories for Model Context Protocol servers/clients).
- **30+ CVEs filed against MCP servers/clients/infra in Jan–Feb 2026** (Cycode).
- **Palo Alto Unit 42: 78.3% attack success rate** across a 5-MCP-server test environment.
- **NSA released an MCP security guidance PDF (June 2026)** — "Unverified task propagation" etc.
- Academic threat model (MDPI, May 2026): **tool poisoning (malicious instructions in tool metadata) is the most prevalent client-side MCP vulnerability**.
- Snyk ships a **free `mcp-scan` tool** for vetting MCP servers.
- AI-hallucination squatting (fake package names generated by models) is a named 2026 agentic attack vector — SEB's garak `packagehallucination` probe already covers part of this.

**→ SEB should add an MCP tier/probe class and map to the OWASP MCP Top 10. CK Catalyst's public `/.well-known/mcp.json` is a live, authorized test target.**

### Engine landscape (2026)
- **garak** (NVIDIA, Apache-2.0): 8.6k stars, 4,481 commits, extremely active (PRs merged same week). Probe families: `promptinject`, `dan`, `encoding`, `leakreplay`, `latentinjection`, `malwaregen`, `packagehallucination`, `xss`, `pii_extraction` (SEB contributed). Talks to 20+ backends incl. generic `rest` generator for your own API. **SEB has 0.15.1 installed — newer than the v0.14.0 that public reviews describe.**
- **PyRIT** (Microsoft, MIT): ~4k stars, 117 contributors. Depth pass: **multi-turn Crescendo, TAP, Skeleton Key** — exactly what single-shot scanners miss. Workflow of record: *garak breadth pass → triage → PyRIT depth pass* (SecurityCipher, Jul 2026).
- **Giskard** (Giskard-AI, open source): v3 is now a **modular architecture wrapping any LLM, black-box agent, or multi-step pipeline** — better fit for SEB's agentic tier than the old v2 monolith.
- **Promptfoo** (OpenAI, acquired **2026-03-09**): MIT license stays; Cloud roadmap folded into OpenAI Frontier. Remains a DIY competitor, not a service.
- **NEW OSS: DeepTeam** (confident-ai/deepteam, Apache-2.0): framework with **built-in OWASP ASI 2026, NIST AI RMF, MITRE ATLAS, EU AI Act detection** — the closest new OSS analogue to what SEB sells as a service. Watch it; consider it a reference engine for the agentic tier.
- **NEW OSS: Wallbreaker** (JailbrokenAI/wallbreaker): fetches L1B3RT4S + P4RS3LT0NGV3 + ENI corpora at runtime, copyleft. Signals the corpora SEB depends on are becoming commoditized — SEB's value must be **human-verified managed service + compliance mapping**, not corpus access.
- **L1B3RT4S** (elder-plinius, 46.6k stars): jailbreak prompt corpus + `!SHORTCUTS.json` — SEB already uses this. **CL4R1T4S** (9.5k stars): leaked system prompts by platform — SEB inventories it but **underuses it: leaked system prompts are a ready-made LLM07/ASI06 probe library per platform.**

### Jailbreak technique taxonomy (2026) — depth your probes should cover
GCG adversarial suffixes · encoding smuggling (base64/ROT13/unicode) · **multi-turn crescendo** · TAP (tree-of-attacks) · **Skeleton Key** · many-shot · fake-policy injection · refusal suppression · persona splits · low-resource languages · multi-modal payloads · indirect/latent injection in RAG/tool output.

### Agentic red-teaming best practice (2026)
- **Test the whole application, not the raw model** — guardrails, RAG context, and tools are where real bugs live (SecurityCipher; requie/AI-Red-Teaming-Guide).
- **Tie detection to agent telemetry** (tool calls, network egress), not just prompt content — this is how agentic findings become provable.

---

## 3. Severity-Ranked Gap Analysis

### 🔴 CRITICAL — fix first

**C1. Cron model pinning violates SEB_MODEL_GUARD + Malik's fallback directive**
- Evidence: all 7 SEB jobs pinned `tencent/hy3` (nous) — the model your own guard calls "LAST resort only" and "FORBIDDEN as primary". Malik's standing rule: cron jobs must use the global fallback chain, not fail on a single pinned model ("That's bad CEO behaviour").
- Fix: rewire all SEB jobs to the chain **nemotron-3-ultra → nemotron-3-super → openrouter/gpt-oss-20b:free → step-3.7-flash:free → hy3:free** (primary where available, hy3 only as last resort). Update SEB_MODEL_GUARD.md, PROFITABILITY_PLAN.md, and the cron registrations to match. Keep `SEB_MODEL_GUARD` hold/alert behavior on the intel pipeline.
- Accept: `hermes cron list` shows the chain; a forced run on each job succeeds; model-guard doc and reality agree.

**C2. Heavy engines never fire — dogfood is only L1B3RT4S**
- Evidence: `_try_garak/_try_pyrit/_try_giskard` all append "skipped" for any non-HTTP target. Every dogfood run uses `DefendedSimTarget` (a Python callable) → garak/pyrit/giskard always skipped. 74-probe dogfood ≠ the "100+ probes / 4 tools" you sell.
- Fix: build **`test_harness.py`** — a local FastAPI/Flask server that wraps `DefendedSimTarget`/`VulnerableSimTarget` on `localhost`, then:
  - garak via `rest` generator (see §5 for the current garak 0.15.x config format — your `_try_garak` uses an outdated generator config shape: current format is `-G rest_target.json` with `RestGenerator { req_template_json_object, response_json_field }`).
  - PyRIT `PromptSendingOrchestrator` + Crescendo/TAP converters against the same endpoint (single + multi-turn).
  - Giskard `AgenticEvaluator` against an agent wrapper (start with the sim agent; expand to real agent frameworks later).
- Accept: dogfood run reports **0 skipped engines** and >200 probes; defender target still yields 0 findings; vulnerable target yields findings from all 3 engines.

**C3. `intel_log` table is always empty**
- Evidence: `client_db.log_intel()` exists; `pipeline_intel.py` never calls it; table has 0 rows despite daily runs.
- Fix: call `log_intel()` in `pipeline_intel.main()` with source/commit/new_classes/run_time_ms; keep the ESCALATIONS.log + queue behavior.
- Accept: next intel run inserts a row.

**C4. Credibility-gate decision is due (~Aug 4)**
- Evidence: 3 OSS PRs open since 07-10/07-14, 0 merged; STRATEGY.md funded fallback = Certified AI Security Professional (~$200, 20–40 hrs) "if PR not merged within 3 weeks" (from 07-14 → due 08-04).
- Fix: build a **gate-status block** into the daily digest (PR statuses + days-open + fallback deadline), escalate to Klaus for Malik's decision before Aug 4. Do NOT start paid outreach on unauthorized leads until gate clears (SOUL §9).

### 🟡 HIGH — next

**H1. Add OWASP MCP Top 10 coverage (new market wedge)**
- Build: `MCP_TOP_10` reference table in scorer.py (10 categories, per OWASP June 2026 release); new attack classes (`mcp_tool_poisoning`, `mcp_prompt_injection`, `mcp_auth_bypass`, …) mapped to MCP-01…10 + ATLAS + CVSS; a `mcp_scan` probe path (Snyk `mcp-scan` or manual GET of `/.well-known/mcp.json` + tool-list + injection-via-tool-description, **authorized targets only**); MCP section in report_generator; MCP badge on landing page; MCP add-on tier in PRICING.md.
- Test target available NOW: **CK Catalyst's public MCP server** (authorization on file).
- Accept: an authorized MCP scan produces MCP-mapped findings and a PDF section.

**H2. Run the authorized ACTIVE phase for CK Catalyst**
- Evidence: passive Quick Scan delivered 07-27 (MODERATE 45/100); authorization on file; active OWASP LLM Top-10 probing explicitly within scope; invoice pending.
- Fix: run full gauntlet (L1B3RT4S + garak + pyrit + giskard + MCP) against the endpoints listed in the authorization record; deliver active-phase report; move engagement to delivered; then escalate invoice to Klaus → Malik (payment account, P0.6).
- Accept: engagement row with findings persisted, PDF delivered, invoice issued.

**H3. Commit the uncommitted working tree**
- Evidence: git log stops 07-14; working tree has 7+ files newer (email_compiler.py, email_templates/, msp_pitches.md, risk_scores.md …).
- Fix: `git add -A`, commit in logical chunks with descriptive messages (docs, tools, intel artifacts).
- Accept: `git status` clean; `git log` current.

**H4. Fix the pricing/doc conflict**
- Evidence: landing page ($500/$2,500/$2,000-mo) vs PRICING.md ($500/$500-mo/$2,000, Malik-confirmed 07-12).
- Fix: align landing page + PRODUCT.md + outreach templates to PRICING.md; add the retainer tier to the landing page; note the planned retainer migration to $1.5K–2K/mo (STRATEGY.md Pillar 3) as a roadmap item, not current pricing.
- Accept: every client-facing artifact shows the same three tiers.

**H5. Pivot lead-gen to AI-native companies**
- Evidence: risk_scores.md — 0/33 Kelowna SMBs have a public AI chatbot; only CK Catalyst (AI-services) is ICP-fit; Jul-22 escalation already recommended the pivot.
- Fix: build a prospect list of AI-native companies (SaaS with public chatbots/agents, A2A/MCP/OpenAPI surfaces, LLM tool builders); use **CL4R1T4S platform list as a signal source** (any company on a platform with leaked prompts is a candidate); re-run the risk-score rubric on the new cohort; keep the auth-gate — drafts only for authorization_given=1.
- Accept: new cohort scored in risk_scores.md; ≥5 ICP-fit leads identified; 0 unauthorized contacts.

**H6. Deploy the landing page + make the intake form real**
- Evidence: `landing/index.html` built 07-10, never hosted; intake is client-side only (downloads JSON + mailto) — there is **no way to receive the authorization record programmatically**.
- Fix: deploy to GitHub Pages or Cloudflare Pages (free); wire the intake form to a backend endpoint or form service that stores `authorization_record_*.json` into `authorizations/` (or document the manual drop-in path); end-to-end test the flow.
- Accept: public URL serves the page; a test submission yields a stored authorization file.

### 🟠 MEDIUM — engineering debt

- **M1. Productize the risk-score tooling**: `_assess.py`/`_build_leads.py`/`_sync_leads_db.py` are underscore scripts — promote to `pipeline_risk_score.py` (+ unit tests) and let the cron call it.
- **M2. Retainer finding-dedup**: compare by `attack_class + owasp_id + evidence hash`, not title only; track NEW → PERSISTING → REGRESSED → FIXED lifecycle (pipeline_retainer.py currently title-only).
- **M3. Scope-lock hardening**: in `_load_authorization`, reject if the target URL differs from the auth record; log a scope-mismatch escalation instead of scanning (STRATEGY.md Pillar 7).
- **M4. HackerOne account + Good Faith AI Research profile** (V3 Phase 3 item 7 — still not done).
- **M5. Dogfood #2 vs Klaus's SOUL.md** → second portfolio piece; regenerate the portfolio PDF (V3 item 8).
- **M6. notify.py event coverage**: add `model_fallback_triggered`, `authorization_expiring` (30/7/1-day), `cron_job_failed` (after 3 retries).
- **M7. Report upgrades**: MCP section (H1), severity-over-time trend for retainers, executive one-pager, NIST AI 600-1 + ISO 42001 mapping lines, "State of Agentic AI Security" (OWASP, June 2026) and AIUC-1 crosswalk citations.
- **M8. CL4R1T4S utilization**: turn leaked system prompts into per-platform `system_prompt_leak` probe sets (authorized targets only) — direct LLM07/ASI06 coverage.

### 🟢 LOW — growth & credibility

- **L1. MCP/agentic probe contributions upstream** (garak probe PRs) — compounds credibility AND builds the STRATEGY.md Pillar 5 proprietary probe pack.
- **L2. Annual "SMB AI Risk Benchmark"** from authorized-scan data (Pillar 5 moat).
- **L3. "State of AI Red Teaming" blog post + BSides Vancouver / OWASP talk** (V3 ongoing #20).
- **L4. AI-BOM** (OWASP AI SBOM initiative) as a report feature for supply-chain clients.
- **L5. Watchlist**: DeepTeam (new OSS analogue), Wallbreaker (corpus commoditization signal), Promptfoo→OpenAI Frontier (Cloud roadmap), Mindgard/Lakera pricing moves.

---

## 4. What's Strong — Do Not Break

- **"No fake it" architecture** — honest engine-skip reporting, dry-run invoices, queued escalations. This is rare and is the trust moat.
- **CFAA/legal posture** — auth-gate in code, rate limits, fail-fast, no third-party infra probing, HackerOne Safe Harbor framing. Keep every guard.
- **Standards accuracy** — OWASP LLM 2025, ASI 2026, ATLAS 16/173 all verified correct against authoritative sources.
- **Defense-aware detector** — refusal ≠ finding; leak markers + human-triage gate.
- **Test isolation** — 12 tests never touch prod DB/PDF paths.
- **Delivery discipline** — CK Catalyst engagement was scoped, authorized, delivered, and invoiced correctly.
- **Escalation wiring** — Telegram live, queue drained, human-readable ESCALATIONS.log for un-blindness.

---

## 5. Reference: current garak 0.15.x REST config format

(Your `_try_garak` uses an outdated generator config; garak ≥0.14 accepts `-G <config.json>` with this shape — verified against the July 2026 garak+PyRIT workflow guides.)

```json
{
  "rest": {
    "RestGenerator": {
      "uri": "http://127.0.0.1:8765/test",
      "method": "post",
      "headers": { "Content-Type": "application/json" },
      "req_template_json_object": { "prompt": "$INPUT" },
      "response_json": true,
      "response_json_field": "response"
    }
  }
}
```

```bash
garak --target_type rest -G rest_target.json --probes promptinject,dan,encoding,leakreplay,latentinjection,packagehallucination,pii_extraction
```

---

## 6. Priority Execution Checklist (next 7 days)

| # | Task | Severity | Est. effort |
|---|---|---|---|
| 1 | Rewire 7 SEB crons to fallback chain; reconcile model-guard docs | 🔴 C1 | 1 hr |
| 2 | Build `test_harness.py`; wire garak (new config) + PyRIT + Giskard; dogfood with 0 skips | 🔴 C2 | 1–2 days |
| 3 | Wire `log_intel()` into pipeline_intel | 🔴 C3 | 30 min |
| 4 | Gate-status block in daily digest; escalate cert decision before Aug 4 | 🔴 C4 | 1 hr |
| 5 | OWASP MCP Top 10: scorer table + probes + report section + pricing | 🟡 H1 | 1–2 days |
| 6 | CK Catalyst active phase (authorized) + invoice | 🟡 H2 | 1 day |
| 7 | Commit working tree; fix pricing conflict; deploy landing page | 🟡 H3/H4/H6 | 1 day |
| 8 | Pivot lead cohort to AI-native companies; re-score | 🟡 H5 | 1 day |
| 9 | M1–M8 debt items | 🟠 | ongoing |

## 7. Key Sources

- OWASP Agentic 2026 (official): genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- OWASP LLM Top 10 2025: genai.owasp.org/llm-top-10/
- MITRE ATLAS: atlas.mitre.org
- OWASP MCP Top 10 coverage: cycode.com/blog/owasp-mcp-top-10/ · NSA MCP CSI (June 2026) · Snyk mcp-scan
- garak: github.com/NVIDIA/garak · garak.ai
- PyRIT: github.com/Azure/PyRIT · appsecsanta.com/pyrit
- Giskard v3: github.com/Giskard-AI/giskard-oss
- Promptfoo→OpenAI (2026-03-09): promptfoo/promptfoo
- DeepTeam: github.com/confident-ai/deepteam · Wallbreaker: github.com/JailbrokenAI/wallbreaker
- L1B3RT4S / CL4R1T4S: github.com/elder-plinius
- Market: thebusinessresearchcompany.com (AI Red Teaming Services 2026–2030) · technavio.com (Solutions 2026–2030)
- EU AI Act Omnibus: gibsondunn.com (May 2026) · digital-strategy.ec.europa.eu
- HackerOne Safe Harbor: hackerone.com press release, 2026-01-20
- NIST AI 600-1: nist.gov (July 2024)
- 2026 jailbreak taxonomy: wraith.sh/learn/llm-jailbreak-guide · razmsec.com/blog/jailbreaking-llms-techniques-taxonomy-2026 · crescendo-the-multiturn-jailbreak.github.io
- Agentic RT practice: requie/AI-Red-Teaming-Guide · securitycipher.com (garak+PyRIT workflow, 2026-07-15)
