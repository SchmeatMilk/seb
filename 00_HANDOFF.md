# SEB — Context Handoff (from Klaus session, 2026-07-09)

> Read this to pick up where today left off. Full detail lives in the linked plan docs (paths in SOUL.md §11). This is the "what happened + where to start" summary.

## What Malik and I built today (2026-07-09)

### SEB concept (the whole point)
- **SEB = Security Inquisitor Balance** — an autonomous AI-security firm Malik will own and run solo, via Hermes cron + OpenCode Zen (free tier).
- Modeled after Ernest/Brok as a sub-agent under Malik, but SEB is its own business, not a content/sales function.
- Delivers adversarial prompt testing, agent hardening, continuous monitoring as a service.

### Research done (3 parallel sub-agents + 10 self-critique passes)
1. **Competitive landscape** → `~/src/agent_company/docs/seb-competitive-landscape.md` (17K)
   - $500 entry is uncontested. Nearest managed competitor = $5K (AI Vyuh). Boutique = $12K+ (DSE).
2. **Business viability / gap analysis** → `~/src/agent_company/docs/SEB_GAP_ANALYSIS.md` (16K)
   - v1 legal framework was a **liability bomb** (CFAA, third-party infra, "fake it" voice, no certs).
   - SMB willingness-to-pay overestimated; OSS tools (Garak/PyRIT) commoditize the $500 audit.
3. **Refined plan** → `~/src/agent_company/docs/SEB_PLAN_V2.md` (48K)
   - 4-tier pricing (Free → $500 → $2,500 → $2K/mo).
   - Fleet architecture, pipelines, rewritten legal section, launch gates.

### Key decisions baked into the plan
- Deleted the "fake it" brand voice. SEB is transparent.
- Rewrote legal around **HackerOne Good Faith AI Research Safe Harbor** + third-party-infra scope limits.
- Bumped middle tier $1,500 → $2,500.
- SEB-SALES is **authorization-only** — no unauthorized scanning.
- Credibility gate: ≥1 cert OR OSS PR before first paid client.

## Where to start (Phase 0 → 2 of SEB_PLAN_V2.md)
1. `~/src/seb/` already created (workdir).
2. Init SQLite `clients.db` (schema in plan Appendix C).
3. Code `gauntlet.py` (multi-tool: Garak + L1B3RT4S + PyRIT + Giskard).
4. Code `scorer.py` (OWASP LLM Top 10 + CVSS 4.0 mapping).
5. Dogfood against a test target → produce a valid PDF.
6. Credibility: enroll OWASP LLM Testing cert OR submit a Garak/L1B3RT4S PR.

## Open items for Malik
- Approve Phase 0 build start.
- Sophia decision (deadline Aug 1) and re-contacting Saji/Ben — separate from SEB, on his plate.
- Bankruptcy constraint: build assets now, defer income until discharge (Nov 2026).

## Directories / files that exist right now
- `C:\Users\mbapt\src\seb\` — created, empty except this handoff.
- `C:\Users\mbapt\AppData\Local\hermes\profiles\seb\` — the profile (config, .env, SOUL.md, skills cloned from ernest).
- `~/src/agent_company/docs/SEB_PLAN_V2.md` — the master spec.
