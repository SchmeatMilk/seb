# SEB — Future Growth Plan (v2, POST-CRITIQUE REVISION)

> Rewritten after independent critic scored v1 = 2.68/5 (FAIL). All 5 fatal
> flaws (F1–F5) addressed. Critic context: C1=4,C2=3,C3=2,C4=2,C5=3,C6=1,C7=3,
> C8=3,C9=4. This version fixes C3, C4, C6 and the 5 flaws.
> Client-facing claims remain DRAFTS → require Brok/Malik sign-off (SOUL §4b).

**Goal:** Make SEB a revenue-generating, credible AI-security firm that runs
mostly on autonomous agents — within the hard rules. This version is HONEST
about constraints the v1 plan glossed over.

**One sentence for Malik:** We sell cheap, continuous AI safety check-ups to
small businesses using robots that do most of the work, in a market growing
~28%/yr — but we must FIRST earn the right to charge (clear the credibility
gate) and we must be realistic that the first paying clients will be few, not many.

---

## 0. Hard truths the research forced (carried from v1, unchanged facts)
- Market: $2.26B(2026)→$6.17B(2030), ~28% CAGR. Competitors consolidated into
  expensive platforms → gap for low-cost boutiques (our niche).
- Pricing reality: boutique AI assessment $12K–$18K; full red-team $35K–$55K;
  retainer from $8.5K/mo; entry posture from $1.5K. SEB is far below market.
- Acquisition: referrals 58% + content/inbound 27% >> cold outreach (low yield).
- EU AI Act high-risk DEFERRED to 2 Dec 2027 / 2 Aug 2028. Aug 2026 = transparency
  only. Demand ramps 2027–2028, not 2026. NIST AI RMF + ISO 42001 are live now.

---

## PILLAR 1 — Clear the credibility gate (OWNED, FUNDED)  [fixes F1]
SOUL §9 forbids ANY paid client until the gate is cleared. This is the #1
blocker; everything else is moot until it's done. So it gets a named owner and
a funded fallback — not a hope.

- **Owner:** Klaus (operational manager) drives; Malik approves spend.
- **Primary path:** PR #1963 at NVIDIA/garak (open, 4/4 pass). Monitor weekly.
  Escalate to Klaus if rejected twice.
- **Funded fallback (triggered if PR not merged within 3 weeks):** enroll Malik
  in a RECOGNIZED cert — e.g. **Certified AI Security Professional**
  (Practical DevSecOps, ~$200, ~20–40 hrs study). Budget: $200 + Malik's time.
  This is a real cost and a real time drain — accounted for, not "cost TBD."
- **Exit criteria:** gate = PASSED the day PR merges OR cert is obtained. No
  revenue activity (even outreach that implies paid work) before this.
- **Why funded not hoped:** the gate is outside our control (NVIDIA's merge
  decision). We do NOT bet the business on it — we buy the cert insurance.

## PILLAR 2 — Honest revenue model (bottom-up, not fantasy)  [fixes F2]
Rebuild from reality, not targets:
- 33 existing leads are unqualified/unauthorized (0/33). Treat as a weak list.
  Realistic yield: 33 × 10% re-qualified opt-in ≈ **3 clients** over 90 days,
  IF the gate is cleared. Not 10.
- **Primary channel is NOT cold outreach.** Per research, referrals (58%) +
  content/inbound (27%) win. So:
  - Build a plain-language content engine ("Is your AI safe?") seeded by the
    garak OSS story (novel, PR-worthy) → inbound over Wk 4–12.
  - Pursue 1–2 MSP partnerships (real contracts, not a cron) for volume.
  - Cold touch to the 33 only as re-qualification, post-gate, post-sign-off.
- **Realistic 90-day KPIs:** gate PASSED; 2–4 paying clients (Quick Scan or
  small audit); 0–2 retainers; first case study. NOT 10 retainers.
- **12-month KPIs (post-demand-ramp):** 8–15 clients; 3–6 retainers; first MSP
  white-label live. Conservative, survivable.

## PILLAR 3 — Price for margin, account for human labor  [fixes F3]
The v1 "near-zero marginal cost" claim is FALSE: SOUL §4b + §7 require every
client deliverable to be human-reviewed (Brok) and signed off. That is real
labor. So:
- Keep $500 Quick Scan as a LOSS-LEADER / lead hook (market entry floor is $1.5K;
  we undercut deliberately to win first clients).
- Price the **retainer to cover Brok's review time**: at $500/mo, assume ~2 hrs
  of Brok review/reporting/mo → only viable with high automation + few clients
  until we raise price. **Plan: migrate retainer to $1.5K–$2K/mo within 6 months**
  (still < market $8.5K, still profitable, covers human review).
- The moat is NOT "we're cheaper because robots" (that's a price wedge any MSP
  copies). See Pillar 5 for the real differentiator.

## PILLAR 4 — "Readiness," not fake urgency  [addresses C5/timing, F4]
- Sell AI Act / NIST AI RMF / ISO 42001 **readiness**, honestly framed:
  "regulations ramp 2027–2028; getting ready early is cheaper than scrambling."
- NO "Aug 2026 compliance" claims (factually wrong post-Omnibus).
- Align revenue expectations to the 2027–2028 demand ramp; survive the 2026 gap
  with low burn (agents are nearly free; only cert + Malik/Brok time cost money).

## PILLAR 5 — Defensible differentiator (BUILD, not claim)  [corrects overclaim in v2]
v2 asserted a "proprietary probe pack" as existing IP. VERIFIED FALSE (2026-07-14):
the `.l1b3rt4s_clone` and `.cl4r1tas` folders contain 0 Python files — they are
per-vendor PROMPT/RESEARCH collections (notes, jailbreak recipes), NOT garak
probes. Some content even conflicts with SOUL hard rules (no attacks/unauthorized
testing). So the moat is a BUILD TARGET, not an asset we own.

Real, rule-compliant differentiator to BUILD:
- **Author clean garak probes/detectors** (inherit garak base classes, map to
  OWASP/NIST/MITRE) for novel SMB-relevant risks — contributed upstream (cred)
  AND wrapped as a SEB-branded extension. This is genuine, defensible IP we
  create within the rules.
- **Published benchmark/report:** an annual "SMB AI Risk Benchmark" using our
  agent data on AUTHORIZED targets only. Compounds authority + inbound.
- **Speed + price + OSS credibility** as a *supporting* edge, not the whole story.
- NOTE: do NOT build the moat on the existing `.l1b3rt4s_clone`/`.cl4r1tas`
  content — it is not code and partially violates our rules. Start fresh, clean.

## PILLAR 6 — MSP white-label (real partnership, not a cron)  [fixes F2 volume]
- Formalize: pursue 1–2 actual MSP contracts (not just the "msp Wed 14:00" cron).
  SEB scans white-labeled for THEIR clients; they bring volume + trust.
- This is the realistic path to many retainers without SEB doing sales.
- Requires a signed agreement + scoped auth per client (see Pillar 7).

## PILLAR 7 — Governance: scope-lock everything  [fixes F5]
- Every retainer scan is **scope-locked to the written authorization** (specific
  endpoints/models named in AUTH_TEMPLATE). The agent may NOT expand "AI surface"
  beyond what's signed. Misconfig = unauthorized testing (SOUL violation).
- All client-facing → Brok/Malik sign-off (§4b). Klaus escalation on: new attack
  class, CRITICAL retainer finding, pipeline fail x3.
- Add a pre-flight check: retainer cron refuses to run if auth scope missing.

---

## Sequenced timeline (realistic)
- **Wk 1:** Brok sign-off on 4 assets. Decide pricing (start $500 hook → raise).
  Klaus owns gate; start cert enrollment as insurance IF PR not merged in 3 wks.
- **Wk 2–4:** GATE CLEARED (PR merge or cert). Launch content engine + MSP outreach.
  Re-qualify 33 leads (post-gate, post-sign-off) — expect ~3 clients.
- **Wk 5–12:** first paid scans; build proprietary probe pack (Pillar 5); pursue
  MSP contract #1; publish first benchmark teaser.
- **Mo 4–12:** convert to retainers (priced to cover Brok review); scale via MSP;
  ride 2027–28 demand ramp.

## KPIs (honest, measurable)
- **Gate:** PASSED (PR merged OR cert obtained) — hard prerequisite.
- **90-day:** 2–4 paying clients; 0–2 retainers; 1 case study; content engine live.
- **12-month:** 8–15 clients; 3–6 retainers; 1 MSP contract; 1 published benchmark.
- **Credibility:** ≥1 merged garak PR OR recognized cert (gate) + ≥1 proprietary probe pack.

## Open risks (carried + new)
- **R1** Revenue math conservative; 33 leads may yield <3. Mitigated by content +
  MSP, but 2026 will be slow by design.
- **R2** "Agent moat" retired; replaced with proprietary probe pack + benchmark (R5 in v1).
- **R3** Cert fallback costs ~$200 + Malik's ~20–40 hrs. Real, budgeted.
- **R4** EU dates corrected (Dec 2027/Aug 2028). No "Aug 2026" claims.
- **R5** Retainer scan scope-lock enforced in code (Pillar 7) — mitigates SOUL drift.
- **R6** Cash-flow gap 2026: low burn (agents free) + cert/brok-time only costs.

## Files this plan will touch (when executed)
- `src/seb/client_review/` — sign-off queue (4 assets + new marketing).
- `src/seb/landing/index.html` — pricing/positioning (Brok-approved).
- `src/seb/AUTH_TEMPLATE.md` — scope-lock fields for retainer scans.
- `src/seb/notify.py` — escalation already wired to Klaus.
- `src/seb/oss-work/garak/` — PR #1963 monitoring + proprietary probe pack.
- New: `src/seb/content/` engine; `src/seb/msp_outreach/` pitch; `src/seb/benchmark/`.
