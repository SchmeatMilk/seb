# SEB Profitability Implementation Plan

**Owner:** SEB (Security Inquisitor Balance) — autonomous AI-security firm
**Manager:** Klaus (operational); **Final authority:** Malik (owner)
**Model:** primary `nvidia/nemotron-3-ultra-550b-a55b` (NVIDIA) with fallback chain:
`opencode-zen/big-pickle` → `nvidia/nemotron-3-super-120b-a12b` → `step-3.7-flash:free` → `tencent/hy3:free` (last resort)
**Objective:** convert the 10 researched profitability levers into shipped revenue.
**Mandate:** maximize profitability; credibility-gated (no paid client until ≥1 cert OR ≥1 merged OSS PR); authorized-only testing only.

---

## PHASE 0 — BLOCKERS (RESOLVED 2026-07-12, per Malik)

| # | Question | Malik's answer | Effect |
|---|---|---|---|
| P0.1 | Auth template | **YES** — Seb drafts a written OK format; uses it before any test | Unblocks paid work |
| P0.2 | Entity/owner name | **Use Malik's name for everything** (family entity deferred until profitable) | Invoicing under Malik |
| P0.3 | Pricing | **YES** — $500 Quick Scan / $500-mo retainer / $2k deep audit confirmed | Levers 1, 10 locked |
| P0.4 | First prospects | **More is possible** — pull broadly from SmartSMB lead list + Kelowna SMBs | Levers 4, 6 widen |
| P0.5 | Credibility $ | **Free only for now** — OSS PR path; paid certs listed for later (see below) | Lever 3 = PR-only now |
| P0.6 | Payment account | **Escalate to Malik when first payment is due** (Klaus pings Malik) | No blocker to start |
| P0.7 | Legal boundary | **YES** — authorized-only + HackerOne safe-harbor lane | Levers 1, 5 locked |
| P0.8 | Owner-call window | **YES** — only first paid client / legal scope / pricing reach Malik | Escalation confirmed |

**Status:** Phase 0 CLEARED. Seb may begin Phase 1–5. Only P0.6 (payment) pauses at first invoice — Klaus escalates to Malik then.

---

## PAID CERTS LIST (for later, when $ available — P0.5)

Free path active now (OSS PR). When budget allows, pursue in order:
1. **OWASP LLM Testing Guide cert** (~$150) — direct credibility for the offer.
2. **SANS SEC542 (Web App Penetration Testing)** (~$7k) — enterprise-grade, unlocks bigger audits.
3. **OSCP (OffSec)** (~$1.6k) — industry-standard pen-test credential.
4. **CISSP** (~$750 exam) — for enterprise/contract credibility.
5. **AI Security Foundation (ISO/IEC 42001 lead)** — emerging AI-governance credential.

---

## PHASE 1 — Credibility (unlocks paid work)

| Lever | Action | Owner | Cron | Metric |
|---|---|---|---|---|
| 2 | ≥1 merged PR to Garak or L1B3RT4S (real bug/test) | Seb | `SEB oss-pr` Mon 10:00 | 1 merged PR |
| 3 | OWASP cert — DEFERRED to paid list (free PR only now) | — | — | PR merged |

## PHASE 2 — Productize (the offer)

| Lever | Action | Owner | Trigger | Metric |
|---|---|---|---|---|
| 1 | Ship **$500 Quick Scan**: OWASP LLM Top-10 auto scan + report, 48h SLA | Seb | now | PRODUCT.md + template |
| 10 | Tiered ladder: $500 / $500-mo / $2k | Seb | after L1 | PRICING.md |

## PHASE 3 — Lead engine

| Lever | Action | Owner | Cron | Metric |
|---|---|---|---|---|
| 6 | Sync SmartSMB leads → $500 offer drafts | Seb | `SEB daily leads` 09:00 | weekly drafts |
| 4 | Kelowna SMBs w/ public AI chatbots | Seb | leads cron | ≥10 targets |
| 9 | Free "AI risk score" magnet (probe lead URLs) | Seb | `SEB risk-score` 09:30 | auto-scores |

## PHASE 4 — Proof (portfolio)

| Lever | Action | Owner | Cron | Metric |
|---|---|---|---|---|
| 7 | Dogfood: full gauntlet vs Klaus's SOUL.md → published piece | Seb | `SEB intel` 06:00 weekly | 2 portfolio pieces |

## PHASE 5 — Scale

| Lever | Action | Owner | Cron | Metric |
|---|---|---|---|---|
| 8 | White-label $500 scan to local MSPs | Seb drafts, Malik intros | `SEB msp` Wed 14:00 biweekly | 3 pitches |
| 5 | Retainer upsell scan→$500-mo | Seb | `SEB weekly retainer` Mon 08:00 | 1 retainer |

---

## Cron map (final, all on nvidia ultra primary + fallback chain)

| Job | Schedule | Phase |
|---|---|---|
| SEB daily intel | 06:00 | 4 dogfood |
| SEB daily leads | 09:00 | 3 sync+niche |
| SEB risk-score | 09:30 | 3 magnet |
| SEB weekly retainer | Mon 08:00 | 5 upsell |
| SEB oss-pr | Mon 10:00 | 1 credibility |
| SEB msp | Wed 14:00 biweekly | 5 scale |
| SEB daily digest → Malik | 20:00 | reporting |

## Milestones

- **Wk1:** Phase 0 logged → `SEB oss-pr` cron created + first PR drafted → PRODUCT.md/PRICING.md written.
- **Wk2:** PR merged → risk-score live → SmartSMB leads drafted.
- **Wk3:** first $500 scan delivered (authorized target or first client) → portfolio #1 published.
- **Wk4:** retainer upsell live → MSP pitch drafted.
**Exit:** ≥1 paid $500 scan + ≥1 retainer.

## Blocker at payment (P0.6)

When first invoice due: Seb escalates to Klaus → Klaus pings Malik for payment account. No payment = no delivery pause, just notification.