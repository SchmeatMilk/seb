# SEB v2 — Spec: Autonomous, Self-Improving AI Security Business

> Written 2026-08-01, from a full interview-me pass with Malik plus a same-day
> verification pass against real code/docs. Status: DRAFT — awaiting Malik's
> review (see Open Questions). Do not proceed to Plan/Tasks/Implement on the
> new (Sam) work until this is confirmed.

## Objective

SEB is Malik's first autonomous, income-producing AI-run business — genesis
of a longer-term pattern of self-improving, eventually self-replicating AI
ventures he owns and directs but does not operate day-to-day. SEB does the
technical work (find, validate, and report real AI/LLM vulnerabilities); a
new subagent, **Sam**, does whatever selling is needed, signed in Malik's
name until he trusts it enough to sign as itself.

This spec does not restart SEB from zero. It already has a working engine, a
real prospect (CK Catalyst) one step from its first invoice, and a same-day
audit (`BUILDER_REPORT_2026-07-31.md`) with its own prioritized technical
backlog. This spec adds the NEW layer on top: Sam, the autonomy/ownership
boundaries confirmed with Malik, and the long-horizon (year+) self-improvement
roadmap — it points at, rather than duplicates, Klaus's existing backlog.

**Users:** Malik (owner) · eventual paying clients (AI startups / SaaS
companies with public-facing AI products) · Klaus (coordinates, does not
manage SEB — SEB is a peer business unit, not a subordinate) · SEB itself
(the acting/building agent) · Sam (SEB's new outreach subagent).

## Current State (verified 2026-08-01 — treat as ground truth over older docs)

- **Engine:** `gauntlet.py` (L1B3RT4S + garak 0.15.1 + PyRIT 0.14.0 + Giskard
  2.19.2, all installed), `scorer.py` (OWASP LLM 2025 + OWASP Agentic 2026
  ASI01-10 + MITRE ATLAS 16/173 — verified correct), `report_generator.py`,
  `client_db.py` (SQLite `clients.db`), `payments.py` (Stripe, dry-run),
  `notify.py` (Telegram, live since 07-21).
- **Autonomous pipelines already live on cron:** `pipeline_intel.py` (06:00
  daily), `pipeline_leads.py` (09:30 daily), risk-scoring (09:30),
  `pipeline_retainer.py` (weekly Mon 08:00), OSS-PR (Mon 10:00), MSP (Wed
  14:00), daily digest to Malik (20:00). All report cron status "ok."
- **First real prospect:** CK Catalyst — signed authorization on file,
  passive Quick Scan delivered (MODERATE 45/100), invoice pending. **Active
  authorized phase not yet run.** This is the fastest path to "any dollar,"
  likely faster than anything new in this spec.
- **Email infrastructure already exists:** `email_compiler.py`
  (Handlebars-style → HTML+text renderer, deliverability-aware) +
  `email_templates/` (`outreach_authorized`, `outreach_optin`,
  `outreach_inbound`). This is template *rendering* plumbing, not
  copywriting intelligence — see the Sam section below.
- **Known live bugs** (Klaus's own audit, already prioritized in
  `BUILDER_REPORT_2026-07-31.md` §3 — do not re-plan here, just execute):
  - 🔴 All 7 SEB crons illegally pinned to `tencent/hy3`, violating
    `SEB_MODEL_GUARD.md`. Fix: fallback chain nemotron-3-ultra →
    nemotron-3-super → gpt-oss-20b:free → step-3.7-flash:free → hy3:free
    (last resort only).
  - 🔴 garak/PyRIT/Giskard never actually fire — dogfood only exercises
    L1B3RT4S. Needs a local HTTP test harness.
  - 🔴 `intel_log` table never populated (`log_intel()` exists, never called).
  - 🔴 Credibility-gate decision due **~Aug 4, 2026** (3 OSS PRs open, 0
    merged; fallback is a ~$200 cert) — needs Malik's decision imminently.
  - 🟡 New market opportunity: OWASP MCP Top 10 (June 2026) — CK Catalyst
    already exposes a public MCP server as a live, authorized test target.
  - 🟡 Pricing conflict: landing page vs. `PRICING.md` — `PRICING.md` ($500 /
    $500-mo / $2,000) is canonical per Malik's 07-12 decision.
  - 🟡 Lead-gen pivot needed: 0/33 current Kelowna SMB leads have a public AI
    chatbot; only CK Catalyst is actually ICP-fit.

## What This Spec Adds (new work, on top of the above)

1. **Sam** — SEB's own outreach subagent, a deliberate partial clone of Brok
   (Malik's SmartSMB marketing manager) — voice and doctrine only, not his
   memory or org position. Full lineage audit lives in Sam's own `SOUL.md`
   (see Current State on Sam, below).
2. **Autonomy governance** — the financial/outreach/code-modification
   boundaries confirmed with Malik (see Boundaries).
3. **Long-horizon roadmap** — staged self-improvement (surface-level now →
   full autonomous self-rewriting later), open-ended timeframe (year+).

## Current State on Sam (verified 2026-08-01)

Sam's identity is now written: `AppData\Local\hermes\profiles\sam\SOUL.md`.
Key facts established there, summarized here so this spec doesn't drift out
of sync with it:

- **What actually makes Brok's emails good, found by reading his SOUL.md
  directly (not a guess):** a documented voice ("short, clipped, polished,
  persuasive... no warmth that isn't calculated"), a named doctrine
  ("4-sentence killer + psychology layer + multi-touch"), a conversion
  toolkit (scarcity, loss aversion, social proof, reciprocity), and one hard
  style rule (no em dashes, hyphens only). This — not any skill file — is
  what got cloned into Sam.
- **The `skills/email/` folder Brok has is a red herring for this purpose:**
  it only teaches the `himalaya` CLI (generic IMAP/SMTP send/read/search,
  MIT-licensed, not SmartSMB-specific). It's genuinely reusable as Sam's
  sending mechanism as-is — no adaptation of `b2b_outbound_sniper` needed
  for sending; that tool isn't part of this build at all now.
- **Deliberately not cloned:** Brok's memory (`brok-memory/`), his
  SmartSMB-specific positioning doctrine and lead-scoring approach, his org
  position (reports to Klaus, closes as backup for Josh). Sam reports to
  SEB, has its own clean memory, and never closes deals.
- **Sam lives inside the SEB tree** — proposed workdir
  `C:\Users\mbapt\src\seb\sam\`, proposed Hermes profile ID `sam` — so the
  whole business unit (engine + its own seller) stays one self-contained,
  separable package, matching the "could sell SEB someday" goal.
- **SEB's existing autonomous lead-discovery pipeline stays as-is and is NOT
  replaced by Sam.** Division of labor: `pipeline_leads.py` /
  `pipeline_intel.py` / the risk-scoring scripts find + score + gate leads on
  authorization (unchanged); Sam writes what actually gets sent once a lead
  is authorized and Malik-approved. Sam does not discover leads.
- **Sam reuses SEB's own existing sign-off mechanism** (SEB's `SOUL.md`
  §4b: draft → `client_review/` queue → approval → send) rather than
  inventing a new one — scoped so Malik, not Brok, is Sam's sole approver.

## Assumptions Being Made (flag any of these that are wrong)

1. **`klaus_hq\AGENTS.md` needs a real update** once Sam exists — it
   currently has no entry for a SEB-owned agent and describes Brok as
   SmartSMB-only. Flagged as a required deliverable, not something to
   silently edit without Malik/Klaus sign-off since it's Klaus's file.
2. **SEB's own `SOUL.md` §4b needs a small edit** — it currently names "Brok
   OR Malik" as client-facing sign-off approvers. For Sam's material
   specifically, it should read "Sam drafts, Malik approves" — no Brok, no
   Sam self-approval. Flagged in Sam's `SOUL.md` §6, not yet done, since
   it's a live edit to SEB's own core identity file.
3. **The credibility-gate decision (~Aug 4) and CK Catalyst's active-phase
   run/invoice are NOT part of this spec** — already correctly scoped in
   `BUILDER_REPORT_2026-07-31.md` and more urgent than anything here. This
   spec assumes that work proceeds on its own track, in parallel.
4. **Sam's actual outbound mailbox doesn't exist yet.** Messages sign as
   "Malik, from SEB," but there's no live, deliverable address behind that —
   SEB's planned domain (`seb.security`) was never hosted. Until that's set
   up (with SPF/DKIM/DMARC — see `b2b_outbound_sniper`'s deliverability
   guide for why this isn't optional), Sam can draft into the review queue
   but nothing can actually send.

## Tech Stack

- Python 3.11, isolated venvs: `.venv` (core), `.engines-venv`, `.pyrit-venv`
  (heavy engines kept separate — follow this pattern for Sam's dependencies
  too if they ever conflict with core).
- SQLite (`clients.db`) via hand-rolled `client_db.py` (not an ORM).
- `reportlab` (PDF), `pystache` (email templates), `python-dotenv`, `requests`.
- Security engines: `garak` 0.15.1, `pyrit` 0.14.0, `giskard` 2.19.2 (NVIDIA /
  Microsoft / Giskard-AI — all OSS).
- Orchestration: Hermes agent runtime + Hermes cron (jobs run with
  `workdir C:\Users\mbapt\src\seb`).
- Model: `opencode-zen/big-pickle` primary, per `SEB_MODEL_GUARD.md`, with a
  defined fallback chain — never a single pinned free model. Sam uses the
  same chain (matches Brok's model choice).
- **Sam's stack:** the `himalaya` CLI skill (cloned reference from Brok, MIT,
  generic) for sending; SEB's existing `email_compiler.py` for rendering.
  No new sending infrastructure to build — `b2b_outbound_sniper` is not part
  of this build.

## Commands (verified where possible)

```
Test:      pytest tests/ -v            # from C:\Users\mbapt\src\seb — 12 passing, tmp_path-isolated
Dogfood:   python pipeline_audit.py    # confirm exact invocation before relying on this
```
Exact dogfood CLI flags and cron registration commands should be pulled from
`BUILDER_REPORT_2026-07-31.md` §5-6 rather than guessed here.

## Project Structure

```
src/seb/
  gauntlet.py, scorer.py, report_generator.py, client_db.py,
  payments.py, notify.py                       # core engine
  pipeline_intel.py, pipeline_leads.py,
  pipeline_retainer.py, pipeline_audit.py       # autonomous pipelines (cron)
  email_compiler.py, email_templates/           # template rendering (existing, reused by Sam)
  _assess.py, _build_leads.py, _sync_leads_db.py,
  _outreach_template.md                         # lead-scoring scripts (Klaus flagged for
                                                 # promotion to pipeline_risk_score.py — not this spec)
  authorizations/, client_review/, intel/,
  landing/, templates/, output/                 # data & delivery artifacts
  oss-tool/, oss-work/                          # OSS credibility work (Garak/L1B3RT4S PRs)
  tests/, clients.db
  .venv/, .engines-venv/, .pyrit-venv/
  SEB_MODEL_GUARD.md, PRICING.md, PRODUCT.md, STRATEGY.md,
  PROFITABILITY_PLAN.md, 00_HANDOFF.md, 01_ONBOARDING_PROMPT.md,
  BUILDER_REPORT_2026-07-31.md, SEB_V2_SPEC.md  # this document

src/seb/sam/                                    # NEW — proposed
  (copywriting logic + himalaya wiring, structure TBD in the Plan phase)

AppData/Local/hermes/profiles/
  seb/                                          # existing — SEB's "mind"
  brok/                                         # existing — SmartSMB only, NOT touched
  sam/                                          # NEW — SOUL.md written 2026-08-01;
                                                 # config.yaml/workdir/registration still to do.
                                                 # workdir -> src/seb/sam/, fresh memory scoped to SEB,
                                                 # model config cloned from brok/config.yaml
```

## Code Style

Match what's already there — e.g. `scorer.py`:
```python
"""
SEB — response scoring engine.
...
Hard rule: SEB never fabricates findings. The detector is heuristic and
conservative; human review (SEB-CORE triage) is the final gate before
any paid deliverable.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional

TAXONOMY = {
    "godmode": {
        "owasp": "LLM01",
        "owasp_name": "Prompt Injection",
        ...
    },
    ...
}
```
- Module docstring states purpose + any hard/non-negotiable rule up front.
- `from __future__ import annotations`, type hints throughout, `dataclasses`
  over ad-hoc dicts for structured records.
- Comments justify *why* (external standard citations, dates, rationale for
  a mapping choice) — not restating what the code does.
- Constants as `ALL_CAPS` module-level dicts for lookup tables.
- New Sam code follows the same style, including a module docstring stating
  its own hard rule (e.g., "never sends without either Malik's per-message
  approval or an explicit graduation flag").

## Testing Strategy

- `pytest`, tests live in `tests/`, isolated via `tmp_path` fixtures — DB and
  PDF output never touch production paths during tests. 12 tests currently
  passing.
- New Sam code follows the same isolation discipline: no test sends a real
  email or touches the real `clients.db`.
- Before Sam sends anything for real, it needs a dry-run mode (mirroring
  `payments.py`'s dry-run-until-keyed pattern) — draft the message, log/
  escalate it, do not send, until explicitly enabled.

## Boundaries

**Always:**
- Gate every actual test on a signed, on-file authorization (existing hard
  rule — unconditional, keep it that way).
- Route every outreach message through Malik for review before send, until
  he explicitly says otherwise.
- Sign outreach as "Malik, from SEB" until Malik explicitly authorizes Sam to
  sign under its own name (separate, independent graduation from the
  review-gate above).
- Escalate to Malik via Telegram on: new attack class discovered, CRITICAL
  finding on a retainer client, any spend request, pipeline failure ×3,
  revenue milestones — extend the existing `notify.py` channel for Sam.

**Ask first (Malik's explicit sign-off, every time, no standing budget):**
- Any spend — API tiers, tools, domains, certifications. SEB/Sam may
  recommend; Malik approves.
- Any change to `klaus_hq\AGENTS.md` or SEB's own `SOUL.md` §4b (not Sam's
  files to edit unilaterally).
- Letting Sam sign outreach under its own name instead of Malik's.
- Letting outreach send without per-message review.
- Any step toward SEB rewriting its own source code/scoring logic/attack
  strategies autonomously — the eventual goal, explicitly staged in, never
  enabled by an agent's own initiative.

**Never:**
- Test any target without a signed authorization on file, no exceptions.
- Scan or attack third-party platform infrastructure (Intercom/Zendesk/
  Drift/etc.) not covered by the client's own authorization.
- Let Sam claim a fabricated track record or inflate findings ("no fake it"
  — existing hard rule).
- Silently degrade to a forbidden model (`tencent/hy3:free` as primary)
  instead of holding and alerting, per `SEB_MODEL_GUARD.md`.

## Success Criteria

1. Sam exists as a working subagent that drafts outreach copy at the quality
   Malik explicitly wants preserved from Brok, routed through SEB's existing
   `email_compiler.py` rendering.
2. Every message Sam drafts is reviewed and signed by Malik before send,
   with a clear, visible path to relax that (per-message review →
   autonomous; Malik's-name → Sam's-name) that only Malik triggers.
3. `klaus_hq\AGENTS.md` and SEB's `SOUL.md` §4b both reflect Sam's existence.
4. No financial action (spend or invoice) happens without Malik's explicit
   sign-off, logged the same way existing escalations are.
5. (Pre-existing, tracked in `BUILDER_REPORT_2026-07-31.md`, not new here,
   but the real near-term win) CK Catalyst's active phase runs and gets
   invoiced — likely SEB's actual first dollar, on its own track.
6. Long-term, unscheduled: SEB demonstrably absorbs new attack
   research/technique classes without manual `scorer.py` edits
   (surface-level self-improvement) — first concrete milestone toward full
   autonomous self-rewriting.

## Open Questions

1. Is `C:\Users\mbapt\src\seb\sam\` / Hermes profile ID `sam` an acceptable
   structure, or is a different location preferred?
2. What email address/domain does Sam actually send from once Gate A/B
   release? Needs Malik's decision plus real deliverability setup (SPF/
   DKIM/DMARC) before Sam is anything but draft-only.
3. Should this spec, and Sam's `SOUL.md`, be referenced in `00_HANDOFF.md`'s
   reading order for future sessions/agents, or kept separate?
4. Who actually makes the two `SOUL.md` edits this spec flags (AGENTS.md,
   SEB `SOUL.md` §4b) — Malik directly, or SEB/Klaus once they're briefed?
