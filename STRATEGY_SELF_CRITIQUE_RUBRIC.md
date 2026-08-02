# SEB Strategy — Self-Critique Rubric

This rubric is the spine of the self-critiquing system. The plan is scored by an
INDEPENDENT critic (a fresh subagent with no access to the author's reasoning,
only the plan + business facts) and then by the author. Each criterion is
scored 1–5 (5 = excellent). A criterion scoring <3 is a MUST-FIX.

Weighted so the things that actually kill a 1–2 person firm (feasibility,
revenue reality, compliance) outweigh cleverness.

| # | Criterion | Weight | What "good" looks like |
|---|-----------|--------|------------------------|
| C1 | **Specific & actionable** | 1.0 | Concrete steps, named owners, dates, file paths. No "leverage synergies". |
| C2 | **Feasible for 1–2 people + free agents** | 1.5 | Everything is doable with no paid team, free/low-cost tooling, the existing autonomous-agent setup. Flags any step needing money/hire we don't have. |
| C3 | **Differentiated / real moat** | 1.0 | Uses SEB's actual edge: the "company of agents" (autonomous, near-zero marginal cost) + garak OSS credibility. Not a me-too pentest shop. |
| C4 | **Clears the credibility gate** | 1.5 | Explicitly resolves SOUL §9 (OSS PR merge OR cert) so paid clients are allowed. No plan that assumes revenue before the gate is passed. |
| C5 | **Compliance-demand aligned** | 1.0 | Ties offerings to REAL obligations: EU AI Act high-risk deferred to 2 Dec 2027 / 2 Aug 2028 (Aug 2026 = transparency only), NIST AI RMF + GenAI Profile (red teaming required), ISO/IEC 42001, US state laws. No false "Aug 2026" urgency. |
| C6 | **Revenue model is sound** | 1.5 | Recurring (retainer) > one-off; realistic conversion math from the 33 leads; shows path to MRR. Not fantasy numbers. |
| C7 | **Respects hard rules (SOUL)** | 1.5 | No live/unauthorized testing, authorized targets only, Brok/Malik sign-off on client-facing, Klaus escalation. Plan must not violate any. |
| C8 | **Execution-ready & tracked** | 1.0 | Has measurable KPIs, a sequenced timeline, and plugs into the existing cron/agent system (intel/leads/risk/retainer/msp). |
| C9 | **Owner-comprehensible** | 1.0 | Malik (non-dev) can read the summary and know what to say "go" to. Plain language, clear decisions. |

**Scoring math:** weighted avg = Σ(score×weight) / Σ(weight). Pass threshold = 3.5.

**Critic instructions (given to the independent subagent):**
- You are a skeptical board advisor to a 1–2 person AI-security startup. The plan
  below is proposed by the founder's AI. Your job is to BREAK it, not praise it.
- Score each criterion 1–5 with a one-line justification.
- List MUST-FIX issues (anything <3, plus any fatal flaw even if scored higher).
- Specifically pressure-test: (a) is the revenue math believable from 33 leads?
  (b) does any step need money/headcount we don't have? (c) does it breach a SOUL
  hard rule? (d) is the Aug 2026 EU AI Act date correct and is the offering mapped
  to a real obligation? (e) is the "agent moat" actually defensible or just vibes?
- Return: scores table, must-fix list, and a one-paragraph "if I were the founder
  I'd kill this plan unless…" verdict.
