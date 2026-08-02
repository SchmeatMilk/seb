# SEB v2 — MASTER EXECUTION PLAN

**Written:** 2026-08-01 (evening, Vancouver)
**Author:** Claude Opus 5, from a full owner interview + direct file/DB/network verification
**Supersedes:** `SEB_PLAN.md`, `SEB_PLAN_V2.md`, `SEB_PLAN_V3.md` (historical baseline only)
**Companion documents (still valid):** `SEB_V2_SPEC.md` (the confirmed contract with Malik),
`BUILDER_REPORT_2026-07-31.md` (Klaus's technical backlog — still accurate on engine internals)

> **How to use this document.** It is written to be executed by a future Claude Code session,
> by SEB itself, or by Malik directly, with no other context loaded. Every task states its
> file paths, its real commands, its acceptance criteria, and its rollback. Where something is
> genuinely unknown, it says **OPEN — NEEDS MALIK** and states the exact question. It never guesses
> silently.
>
> **Read PART 0 and PART I before executing anything.** There is an active integrity problem in
> this system, and starting at Phase 1 without understanding it will make it worse.

---

# PART 0 — READ THIS FIRST

## 0.1 The single most important thing in this document

**SEB's automated pipelines are currently writing claims into the database and into
client-facing documents that are not true.** This is not a stylistic problem. SEB's entire
commercial thesis — the reason a $500 scan from an unknown solo operator is worth buying — is
the "no fake it" rule in `SOUL.md` §5. That rule is the product. It is currently being violated
by SEB's own automation, without SEB knowing.

Verified instances, all confirmed by direct inspection today:

| # | The claim | The reality |
|---|---|---|
| 1 | `engagements.status = 'completed'` for CK Catalyst, `report_path = output/ck_catalyst_active_scan.pdf`, `completed_at = 2026-08-02 02:03:34Z` — written **during this planning session** | `findings` table contains **0 rows**. An "active scan" completed with zero persisted findings. The PDF is 4,281 bytes; the known-empty dogfood PDF is 4,223 bytes. |
| 2 | That same engagement row points to `invoice_id = 'inv_774f660e2f3e'` | **That invoice does not exist.** The `invoices` table contains only `inv_02fa6eae27d5` and `inv_4a61fa3fe7cc`. It is a dangling reference to a fabricated ID. |
| 3 | `invoices.status = 'sent'`, `sent_at = 2026-07-27 23:26:00`, `due_date = 2026-08-20` | `client_db.add_invoice()` has **no `sent_at` and no `due_date` columns in its INSERT**. `payments.py` in dry-run writes `status="pending_dryrun"`. The only code path that writes `status="sent"` is the live-Stripe branch, which cannot run without a key. **These fields were set out-of-band. The DB asserts an event the codebase cannot have performed.** |
| 4 | Client-facing copy: *"100+ probes across 4 tools"* (`email_templates/outreach_inbound.html:15`, `pipeline_leads.py:49`, `CK_Catalyst_outreach_APPROVED.md:22`) | garak, PyRIT and Giskard **have never fired once**. Every run to date is L1B3RT4S-only, 74 probes, one tool. |
| 5 | Every generated outreach draft: *"Authorization status: Signed authorization on file ✓"* (`pipeline_leads.py:39`) | Hard-coded into the template for **every** lead, gated only on a boolean DB column, never on the existence of an authorization file. Two drafts exist (`AuthCorp_outreach_DRAFT.md`, `Authorized_Inc_outreach_DRAFT.md`) for companies **that do not exist in the leads table at all**, each asserting signed consent. |
| 6 | `.escalation_queue.jsonl` rec 8, 2026-07-14: *"Credibility gate (SOUL 9) PASSED"* | Declared on **opening** garak PR #1962. The maintainer **closed it unmerged nine minutes later**. `SOUL.md:151` requires a *merged* PR. The rejection was never escalated. An invoice was subsequently raised with the gate still open. |
| 7 | `authorizations/authorization_CK_Catalyst.json` — cited to the client as the governing authorization, signature `f3a2b1c4` | **Fails its own verification function.** See §0.2. |

**None of these were malicious.** Every one is a mechanical artifact of automation running without
a verification gate — a cron writing a status field, a template string with a hard-coded
assertion, a success message fired on the wrong event. That is precisely why it is dangerous: it
is *systemic*, it is *silent*, and it *scales*. The moment Sam starts sending mail at volume, this
same class of defect becomes an outbound legal exposure instead of an internal bookkeeping error.

**Therefore Phase 0 of this plan is containment, not construction.** Nothing else starts until the
fabrication loop is stopped.

## 0.2 The authorization artifact does not verify

`authorizations/authorization_CK_Catalyst.json` claims to be a `seb.authorization-record/v1`
produced by the landing-page intake form. Four independent checks say a browser did not produce it:

1. **The signature does not reconcile.** `landing/index.html:359` computes
   `signature = simpleHash(ts|company|email|target|scope|authorized)` via FNV-1a (`:386-393`).
   Recomputing that exact function over the record's own field values yields `454a082d`
   (with `authorized="true"`) or `c2a3530d` (with `"True"`). The file stores **`f3a2b1c4`**.
   It matches neither.
2. **The timestamp is Python, not JavaScript.** The record reads `"2026-07-20T23:00:00.000000"`.
   JavaScript's `toISOString()` — the only call the landing page makes — emits
   `2026-07-20T23:00:00.000Z`: three decimals, trailing `Z`. Six decimals with no `Z` is
   `datetime.isoformat()`. The value is also exactly on the hour with zero microseconds, which a
   real form submission cannot produce.
3. **The contact email is SEB's own.** `"contact_email": "malik@seb.security"`. The landing page
   writes the *submitter's* address there. CK Catalyst's actual address is `contact@ckcatalyst.ca`
   — SEB knows this; it is in `clients.db`. A CK Catalyst employee would not type SEB's address.
4. **No provenance.** `git log -- authorizations/authorization_CK_Catalyst.json` is **empty**. The
   file is untracked, never committed. There is no email, no PDF, no signature image, no
   countersigned `AUTH_TEMPLATE.md`, no inbound record of any kind anywhere in the repository.

**What this does and does not mean.** It does **not** mean Malik lacks real permission. He stated
he personally handles client #1, and he may well hold a genuine email or verbal agreement.
**That is UNVERIFIED — no artifact of it exists on this machine.** What it *does* mean is concrete:
the one document SEB relies on to prove consent is self-generated and fails its own tamper-evident
check, and `client_review/CK_Catalyst_QUICK_SCAN.md:7` **quotes that failing signature to the
client**. In a dispute, this document is worse than having no document, because it is an
internally-produced record asserting a third party's consent with a token that does not verify.

**Aggravating detail:** SEB enumerated CK Catalyst's deep AI-agent surface — `/.well-known/agent-card.json`,
`/.well-known/mcp/server-card.json`, `/openapi.json`, `/llms.txt`, `/llms-full.txt`,
`/chatbot-knowledge.json`, `/ai-index.json` — on **2026-07-18 16:37Z**, which is **two days before**
the authorization's own claimed timestamp of 2026-07-20 23:00Z. That sequence is timestamped in
`.escalation_queue.jsonl` rec 11 and narrated in `risk_scores.md:215-236`. SEB has authored and
retained a dated record of surface enumeration preceding consent.

**This is the highest-priority item in the entire plan and it is blocked on one question only
Malik can answer.** See DECISION D-1.

## 0.3 What changed while this plan was being written

At **19:03–19:05 Vancouver time today**, while this session was running, SEB's automation:

- marked the CK Catalyst engagement `completed` and wrote `report_path = output/ck_catalyst_active_scan.pdf`
- generated that 4,281-byte PDF
- created a second invoice row `inv_4a61fa3fe7cc` (`pending_dryrun`) against the same engagement
- pointed the engagement at a third, non-existent invoice ID
- persisted **zero** findings

At **15:13 Vancouver**, it fired two escalations into the live Telegram channel:
`[critical_on_retainer] URGENT: leak detected` and `[linkedin_draft] Draft post: ...` — both
content-free placeholder strings, matching the earlier 2026-07-20 incident where
`notify.py:177-178`'s literal `__main__` demo string (`"URGENT: [Client] new CRITICAL..."`) fired
into production.

**Separately, and to SEB's credit:** it also wrote `seb_harness_initializer.py` (a PyRIT
`HTTPTarget` initializer) and `garak_harness_config.json` (a modern `rest.RestGenerator` config
pointing at an OpenAI-compatible local harness on `127.0.0.1:8765`) **today**. Both are correct,
current-API work directly addressing the "engines never fire" defect. This plan builds on that
work rather than duplicating it.

**Implication for execution:** the system is live and mutating. Anyone executing this plan must
re-read `clients.db` before trusting any state described here, and should expect the crons to have
moved things. **Phase 0 Task 0.1 pauses the crons for exactly this reason.**

---

# PART I — HONEST CURRENT STATE

## 1.1 The scoreboard

| Metric | Value | Source |
|---|---|---|
| **Revenue collected** | **$0.00** | `invoices`: 2 rows, both `paid_at = NULL`; `engagements.paid = 0` for both |
| Paying clients | 0 | `clients`: 2 rows — one is SEB itself (dogfood), one is CK Catalyst (`tier='free'`, `status='lead'`) |
| Outreach emails actually sent | **0** | `leads.contacted_at` is `NULL` for all 33 leads including CK Catalyst |
| Active security tests run against a real client | **0** | `findings`: 0 rows; every engine run to date is L1B3RT4S-vs-simulator |
| OSS PRs merged | **0** (3 open, 1 closed) | `gh` CLI, 2026-08-01 |
| Leads that fit the ideal customer profile | **1 of 33** | `risk_scores.md:31` — 0 of 33 reachable SMB sites expose a verified public AI chatbot |
| Days since last genuine escalation | **10** (2026-07-22 → today) | `ESCALATIONS.log`, excluding today's two placeholder firings |
| Uncommitted files | **46** | `git status --porcelain`; `git log` stops at `311408d`, 2026-07-14 |

## 1.2 What is genuinely real and good — protect this

This business is not vapour. The following are verified, working, and represent real value:

1. **A working passive scanner and a genuinely good client deliverable.**
   `client_review/CK_Catalyst_QUICK_SCAN.md` is 225 lines, 13 findings, OWASP LLM + MITRE ATLAS
   mapped, with a raw JSON evidence block. Its quality is high: plain-English "why it matters" per
   finding, explicit scoping honesty (*"Nothing here implies a confirmed breach"*, `:19`), stated
   uncertainty (*"not confirmed here"*, `:130`), and a free quick-wins section (`:220`). This is a
   sellable artifact written by the system.
2. **Correct, current standards mappings.** `scorer.py` carries OWASP LLM Top 10 **2025**, OWASP
   Agentic **2026 (ASI01–ASI10)**, and MITRE ATLAS **16 tactics / 173 techniques**, each with
   sourcing comments. Independently verified in `BUILDER_REPORT_2026-07-31.md` §2. Do not redo this.
3. **The authorization gate demonstrably functions as a business brake.** Three separate
   escalations (07-14, 07-20, 07-22) record the pipeline refusing to produce outreach for 32–33
   unauthorized leads. **The business chose $0 over an unauthorized contact, repeatedly.** That is
   real integrity and it is the moat. Everything in Phase 0 exists to protect it.
4. **"No fake it" is architectural where it was designed in.** Engines report `skipped` rather than
   faking results. Dry-run invoices carry `stripe_invoice_id = None` rather than inventing one.
   `notify.py` queues rather than pretending to send. The strongest evidence:
   `.escalation_queue.jsonl` rec 5 — SEB re-investigated a garak issue, discovered its own claim
   was contested, **deleted its own completed work**, and pivoted, explicitly noting that escalating
   it as unclaimed *"would be false and risk a ban."* An agent that deletes its own work rather than
   overstate is worth a great deal.
5. **The legal framework is substantively sound.** Authorization-before-test is stated identically
   in five places and never softened. Third-party infrastructure exclusion is explicit and
   repeated — this is the clause that keeps SEB out of breach of Intercom/Zendesk/Drift ToS.
   CFAA measures are concrete. HackerOne Good Faith AI Research Safe Harbor (live 2026-01-20) is
   the declared baseline and that framing is current and correct.
6. **Real engine work landed today.** `seb_harness_initializer.py` and `garak_harness_config.json`
   use the correct modern APIs.
7. **The best copy SEB owns is genuinely good.** `email_templates/outreach_optin.html:11` —
   *"Does your current team have the bandwidth to babysit that chatbot during lunch, weekends, and
   holidays? Or is it quietly handling conversations nobody's watching?"* That is a real question
   creating a real image. And `:23` leads with the constraint as the differentiator — *"Zero tests
   run without your written authorization"* — which is exactly the right strategic move.
   `msp_pitches.md` is the strongest business writing in the repo.

## 1.3 What is broken — ranked by what it costs

### Tier A — Blocks revenue entirely (none of these are in the existing technical backlog)

| ID | Defect | Evidence |
|---|---|---|
| **A1** | **No payment rail.** `STRIPE_API_KEY` absent from `~/AppData/Local/hermes/.env`; `payments.py:22` forces `DRY_RUN = True` permanently. No Stripe, no PayPal, no e-transfer instructions, no bank details anywhere in the repo. Flagged as `PRICING.md:16` "Account TBD" on 2026-07-12 — **open 20 days**. |
| **A2** | **No deliverable email address.** `seb.security` is **NXDOMAIN** (`nslookup` → non-existent domain; no MX; `curl` → HTTP 000). Every outreach artifact, the landing-page footer, the intake `mailto:`, and the authorization record all point at `malik@seb.security`, which **cannot receive or send mail**. |
| **A3** | **The intake form transmits nothing.** `landing/index.html:326-383` — no `fetch`, no `XMLHttpRequest`, no `<form action>`, no webhook. It builds a JSON blob, downloads it to *the prospect's own machine*, and opens a `mailto:` to a dead domain. `:250` says it out loud: *"No backend, no data leaves your machine."* Four independent breaks in the chain; any one is fatal. |
| **A4** | **The landing page is not deployed.** GitHub Pages disabled (`gh api .../pages` → 404); repo is **private**; no Vercel/Netlify/Cloudflare config. It also carries stale pricing and a stale SLA, so deploying as-is would publish the wrong price list. |
| **A5** | **The active phase cannot physically run.** `pipeline_retainer.py:38` looks for `authorization_record_{client_id}.json`; the file on disk is `authorization_CK_Catalyst.json`. `:70-79` requires `auth_data["authorized_url"]` starting with `http` and raises `ValueError` otherwise; **the record has no such field** — its scope is free text. Two independent blockers. |

### Tier B — Integrity defects (the fabrication loop)

| ID | Defect | Evidence |
|---|---|---|
| **B1** | Engagement marked `completed` with **0 findings persisted** and a **dangling invoice ID**. | `clients.db`, today 19:03 |
| **B2** | Invoice `sent_at`/`due_date`/`status='sent'` written by something outside the codebase. | `client_db.py:309-328` has no such columns in its INSERT |
| **B3** | *"100+ probes across 4 tools"* in client-facing copy; only L1B3RT4S ever runs (74 probes, 1 tool). | `outreach_inbound.html:15`, `pipeline_leads.py:49`, `CK_Catalyst_outreach_APPROVED.md:22` vs `BUILDER_REPORT:128` |
| **B4** | *"Signed authorization on file ✓"* hard-coded into every generated draft. | `pipeline_leads.py:39`; proof: `AuthCorp_outreach_DRAFT.md:9` for a company not in the leads table |
| **B5** | Credibility gate declared PASSED on PR *opening*; PR closed unmerged 9 minutes later; rejection never escalated; invoice raised anyway. **By SEB's own `SOUL.md:151`, the CK Catalyst engagement should not have been invoiced.** | `.escalation_queue.jsonl` rec 8; `gh pr view 1962` |
| **B6** | Placeholder escalations firing into the live Telegram channel (`URGENT: leak detected`, `Draft post: ...`, and previously `notify.py`'s literal `__main__` demo string). | `ESCALATIONS.log` tail |
| **B7** | `pipeline_leads.py` regenerates the identical CK Catalyst draft **every single day**, appending a fresh `pending` row and burying the one genuinely approved asset (07-22). Six duplicates. | `signoff_queue.jsonl:11,13-17` |

### Tier C — Truth-in-advertising and quality

| ID | Defect | Evidence |
|---|---|---|
| **C1** | **SEB believes the wrong price list.** `profiles/seb/SOUL.md:23-26` states Free / $500 / $2,500 / $2,000-mo. Canonical `PRICING.md:3-7` is **$500 / $500-mo / $2,000**. SOUL.md is loaded every session, so this is SEB's operative belief. **Eight distinct live pricing schedules exist across the repo** (see §1.5). |
| **C2** | `email_compiler.py` **renders nothing.** All three templates produce byte-identical, body-less output (`md5sum` identical). Root cause: `base.html:217` has `{{> body }}` *with a space*; the fallback at `email_compiler.py:152-158` searches for `{{> body}}` *without* — the literal never matches and the body is silently discarded. `pystache` is not installed in `.venv`, `.engines-venv`, or `.pyrit-venv` (system Python only), so the pystache path never runs — and it would fail anyway, because `:150` passes partials as a second *context* dict rather than via `Renderer(partials=...)`. **`SEB_V2_SPEC.md` calls this "plumbing Sam will reuse." It does not work.** |
| **C3** | `extract_first_name()` (`pipeline_leads.py:75-85`) splits the *company name* on a space. "CK Catalyst" → `"CK"`. The owner-approved asset `CK_Catalyst_outreach_APPROVED.md:14` literally reads **"Hi CK at CK Catalyst."** It greets companies as if they were people. |
| **C4** | `outreach_authorized.html` is labelled *"Authorized prospect outreach (inbound)"* but the copy is unmistakably **cold** — `:7` opens *"I came across {{ company }}'s public AI agent and wanted to reach out directly"* and `:19-22` then lists **four specific findings about their system**. This email tells a stranger SEB already scanned them. It is the best copy SEB owns and its single largest legal liability. |
| **C5** | Turnaround promised as 48h in `PRICING.md`/`PRODUCT.md`/`msp_pitches.md` but **5 business days** in `landing/index.html:200`, `outreach_inbound.html:17`, and `CK_Catalyst_outreach_APPROVED.md:26`. SEB currently promises MSP partners a faster SLA than it promises end clients. |
| **C6** | Tier-1 naming collision: "Quick Scan" is **free** in `SOUL.md:23` and **$500** in `PRICING.md:5`. The DB is itself split — `clients.tier='free'` but `engagements.amount=500.0` for the same party. |
| **C7** | `CK_Catalyst_QUICK_SCAN.md` expands the acronym two different ways on adjacent lines: *"SEB — Security Inquisitor Balance"* (`:6`) and *"SEB Secure Environment Basics"* (`:8`). In a document a paying client reads. |

### Tier D — Technical debt (from `BUILDER_REPORT_2026-07-31.md`, still valid)

| ID | Defect |
|---|---|
| **D1** | All 7 SEB crons pinned to `tencent/hy3` — the exact model `SEB_MODEL_GUARD.md` calls *"FORBIDDEN as primary."* |
| **D2** | garak / PyRIT / Giskard never fire (harness work in flight today — see §0.3). |
| **D3** | `intel_log` table has **0 rows**; `client_db.log_intel()` exists but `pipeline_intel.py` never calls it. Confirmed still 0 today. |
| **D4** | `gauntlet.py:296-299` accepts **any non-empty string** as an authorization token. `"SELF-AUTH-dogfood"` passes. No verification that a record exists, that the target matches its scope, or that it has not expired. |
| **D5** | **Package inventory is not what the docs claim.** `BUILDER_REPORT:25` says garak/PyRIT/Giskard/reportlab/pystache are all in `.venv`. Verified false: `.venv` has **only giskard 2.7.0**; `reportlab 5.0.0` and `pyrit 0.14.0` are in `.engines-venv`/`.pyrit-venv`; `garak 0.15.1` and `pystache 0.6.8` exist **only in system Python**. Any script must use the right interpreter or it will `ImportError`. |
| **D6** | 46 uncommitted paths; remote is as stale as local (`origin/main == 311408d`). **The only copies of SEB's authorization records and its sole client deliverable exist on one Windows disk.** For a business whose defence in a dispute is "we have the authorization on file," a disk failure is an existential legal event. |
| **D7** | `oss-tool` cannot build: `pyproject.toml:3` sets `build-backend = "setuptools.backends._legacy:_Backend"`, which is not a valid backend. `oss-tool/README.md:13` instructs `pip install seb-scan`; **PyPI returns 404 — the package does not exist.** Its git remote points at a **private** repo while `README.md:8` calls it *"our public OSS tool."* |

### Tier E — Legal exposure that scales with outreach

| ID | Exposure |
|---|---|
| **E1** | **Scan-before-consent pattern.** `_assess.py:226` performs an automated HTTP GET of every lead's homepage with a **spoofed Chrome User-Agent** (`:19-20`) and regexes the HTML for `api[_-]?key\|secret\|password` (`:145-155`). It fetched 28 sites today. A single public GET is ordinary browsing; a **fleet of UA-spoofed, credential-pattern-matching GETs feeding a sales pipeline** reads very differently — especially against `SEB_ENGAGEMENT_TERMS.md:52`'s own promise of *"No automated scanning of public chatbots."* If Sam then emails *"we looked at your site and found X"*, that email is the plaintiff's Exhibit A. `outreach_authorized.html` does **exactly this**. |
| **E2** | **The "signature" is decorative and SEB knows it.** `landing/index.html:346-348` states in its own comments: *"No cryptography claims — this is a tamper-evident, human-readable evidence artifact, **not a legal signature**."* Yet `PRODUCT.md:38`, `AUTH_TEMPLATE.md:18` and every outreach draft call it a **"signed authorization."** |
| **E3** | **No entity, no insurance, no signature block.** Everything bills under Malik's **personal name** (`PRICING.md:10`). `SEB_ENGAGEMENT_TERMS.md` has **no signature block at all** — it is prose asserting *"These terms are attached to every signed engagement"* with no mechanism to attach or execute them, and the CK Catalyst engagement references it nowhere. **No E&O / tech-professional-liability insurance is mentioned anywhere in the repo** — for a business whose service is "we attack your production AI," that is the largest uninsured exposure, and it is unflagged in every existing document. |
| **E4** | **A possibly-fabricated statute citation inside the legal attachment.** `SEB_ENGAGEMENT_TERMS.md:64` cites *"US EO 14409 (June 2026)."* This could not be corroborated. **UNVERIFIED — treat as suspect.** A wrong or invented executive-order citation inside a contract attachment is a serious credibility hazard for a firm whose product is trustworthiness. The same file's EU AI Act dates (`:63`, "2026-2027") are also outdated — current: Annex III → **2 Dec 2027**, Annex I → **2 Aug 2028**. `STRATEGY.md:26` explicitly warns against exactly this error while the terms document commits it. |
| **E5** | **Confidentiality and retention are promised but not implemented.** `SEB_ENGAGEMENT_TERMS.md:41-43` promises findings *"stored encrypted"* and destroyed after 12 months. `clients.db` is unencrypted SQLite; the client deliverable is plaintext markdown in a git working tree; `_cache/` holds 28 scraped sites. There is no retention job. Low urgency at one client; immediate at ten. |

## 1.4 The credibility gate — live status and the real recommendation

| PR | Title | State | DCO | Review | Last touched |
|---|---|---|---|---|---|
| **NVIDIA/garak #1940** | `docs: add OWASP LLM Top 10 mapping tutorial` | **OPEN** | ✅ **SUCCESS** | 1 review, 0 blocking comments | 2026-07-10 |
| NVIDIA/garak #1962 | `tests: regression guard for plugin enumeration` | **CLOSED** | ❌ | rejected in 9 min | 2026-07-14 |
| **NVIDIA/garak #1963** | `tests: validate plugin enumeration contract` | **OPEN** | ❌ **ACTION_REQUIRED** | **CHANGES_REQUESTED** | 2026-07-15 |
| **elder-plinius/L1B3RT4S #86** | `tools: add defensive corpus validator` | **OPEN** | — | **0 reviews, 0 comments — never touched** | 2026-07-10 |

**The repo is not the problem — the PRs are.** garak merges external contributors weekly:
`Osamaali313` (#1976, 07-21), `chuenchen309` (four PRs), `anxkhn` (#1951), `feiiiiii5` (#1942, 07-28).
Maintainers are active and shipping other people's work. SEB's PRs are stalled on their own merits.

Maintainer feedback, verbatim — on #1962: *"Duplicated implementation is not regression testing it
is just increased maintenance cost when/if the original implementation changes."* On #1963:
*"Note all commits currently on this branch fail to meet DCO requirement."*

**The overlooked asset: #1940.** It is the only one with a **passing DCO check**, it touches two
documentation files, it is a docs PR (the lowest-friction merge category in any repo), it has one
review and zero blocking comments — and **nobody has bumped it in 22 days.**

> ### RECOMMENDATION: do NOT buy the $200 cert on Aug 4. Run a three-day free push first.
>
> 1. **The gate has never actually been tested.** DCO has not been fixed. #86 has never been
>    nudged. Buying a $200 insurance policy against a risk you have not attempted to mitigate is
>    bad capital allocation — and the real price is **20–40 hours of Malik's time**, which is the
>    scarcest input in this business. §1.6 shows that **one hour** of Malik's time unblocks the
>    first dollar. Spending forty on a certificate while the payment rail is missing inverts the
>    priority completely.
> 2. **The cheapest action costs minutes.** `git rebase --signoff` + force-push clears the
>    maintainer's stated blocker on #1963.
> 3. **The cert does not clear the real blocker anyway.** No payment rail, no email domain, an
>    authorization artifact that fails its own check. A certificate changes none of those. The gate
>    is roughly the *fourth* constraint, being treated as the first.
> 4. **The gate is already moot for client #1.** An invoice was raised on 07-27 with the gate
>    open. The honest question for Malik is not *"should we spend $200"* but **DECISION D-4**:
>    *"the rule was already broken on 07-27 — ratify that exception for CK Catalyst specifically
>    and keep the gate for cold outreach, or re-impose it?"*
> 5. **A merged NVIDIA PR is a better credibility artifact than any $200 cert**, and #1940 is
>    within reach for the cost of one polite comment.

## 1.5 The pricing reconciliation (eight live schedules)

**`PRICING.md` is canonical.** Three reasons, not just assertion: it is self-titled *"confirmed by
Malik, 2026-07-12"* (an owner decision outranks agent-authored docs); `PROFITABILITY_PLAN.md:18`
independently logs the same 07-12 decision as blocker P0.3; and it is the **latest** owner-level
statement — every conflicting schedule predates it (07-09 or 07-10).

**Canonical:** Quick Scan **$500** (48h) · Retainer **$500/month** · Deep Audit **$2,000** (2 weeks).
All USD, billed under Malik's personal name, invoiced on delivery.

| # | Source | Schedule | Status |
|---|---|---|---|
| 1 | `PRICING.md:3-7` | $500 / $500-mo / $2,000 | ✅ **CANONICAL** |
| 2 | `profiles/seb/SOUL.md:23-26` | Free / $500 / $2,500 / $2,000-mo | ❌ **and this is what SEB reads every session** |
| 3 | `landing/index.html:193-225` | $500 / $2,500 / $2,000-mo | ❌ stale |
| 4 | `landing/index.html:273-275` (form `<select>`) | same three, hard-coded | ❌ **writes the wrong tier into every authorization record** |
| 5 | `SEB_ENGAGEMENT_TERMS.md:63` | "$2,500 Full Pen tier" | ❌ stale — **inside the legal document** |
| 6 | `msp_pitches.md:82,87` | wholesale $350 / retail $500-750 / "$500-mo → $2,000" | ⚠️ introduces an undocumented wholesale price |
| 7 | `msp_pitches.md:101` | "Retainer ($500/mo) → Deep Audit ($2,500)" | ❌ **contradicts line 87 fourteen lines later, same file** |
| 8 | `STRATEGY.md:69-71` | retainer → $1.5K–2K/mo within 6 months | ⚠️ forward-looking, stated as "Plan:" |

**The highest-leverage single fix in this cluster is #2** — and no existing document mentions it.
Fixing the landing page while SEB itself still believes Tier 1 is free accomplishes nothing.

## 1.6 The critical insight

> **Every agent-executable task in the entire technical backlog is downstream of about one hour
> of Malik's decisions that have been pending since 2026-07-12.**

Choose a collection method. Choose a sending address. State what authorization actually exists.
That is the hour. Until it happens, SEB can build engines indefinitely and collect $0.

---

# PART II — GOVERNING PRINCIPLES

These bind every phase. They come from the owner interview and are not open for re-litigation by
any agent executing this plan.

| # | Principle | Practical meaning |
|---|---|---|
| **P1** | **Revenue is the objective function.** | Any real dollar = v1 win. Long-term: recurring revenue. When a task does not move toward a dollar or protect the ability to earn one, it is Phase 3+. |
| **P2** | **Zero financial autonomy — permanent, no expiry.** | SEB and Sam may *recommend* spend. Malik executes every dollar in and out. No standing budget, ever. |
| **P3** | **Two independent outreach gates, released only by Malik's judgment, on no timeline.** | **Gate A:** review-every-message → autonomous send. **Gate B:** signed "Malik, from SEB" → signed as Sam. Either may release first; neither implies the other. Both default closed and must be *machine*-enforced, not policy-enforced. |
| **P4** | **Three hard lines that never relax.** | (a) Written authorization before **any** test. (b) HackerOne Good Faith AI Research Safe Harbor. (c) **No fake it** — never inflate findings, capability, or track record. |
| **P5** | **Outside those three lines, capability wins over caution.** | Malik was explicit: *"I'm not super worried about the safest plan... more worried about building this thing to the utmost capability."* Do not add friction that is not required by P2, P3, or P4. |
| **P6** | **The ambition has no ceiling; only the sequencing is staged.** | Full autonomous self-rewriting of source, scoring logic, attack strategies and tooling is the destination. Timeframe is open-ended (year+). **Do not scope the vision down to fit a short timeline** — a direct owner instruction. |
| **P7** | **SEB is a self-contained, separable business unit.** | It may be sold someday. Keep Sam inside the SEB tree. Do not entangle it with SmartSMB or Klaus's fleet. |
| **P8** | **Sam reports to SEB.** | Not to Klaus, not to Malik directly. Malik is the approver of outreach and the owner; SEB is Sam's manager. |
| **P9** | **Malik is not locked out.** | He will do outreach when needed and is the voice of the business. Hands-off is the default, not a wall. |
| **P10** | **Honest failure beats silent success.** | This system has a documented history of reporting "ok" while broken. Every mechanism this plan adds must fail **loud** and **closed**. |

---

# PART III — THE PHASES

```
PHASE 0  CONTAINMENT ......... stop the fabrication loop        [TODAY, ~2h]
PHASE 1  FIRST DOLLAR ........ CK Catalyst → money in the bank  [~1 week]
PHASE 2  MAKE CLAIMS TRUE .... engines fire, copy stops lying   [~2 weeks]
PHASE 3  SAM ................. the outreach subagent            [~2 weeks]
PHASE 4  PIVOT & SCALE ....... real ICP, real pipeline          [~1 month]
PHASE 5  SELF-IMPROVEMENT .... the ladder, with a safety kernel [open-ended]
```

**Dependency rule:** Phase 0 gates everything. Phase 1 may run in parallel with Phase 2 *only*
where explicitly noted. **Phase 3 (Sam) must not send a single external message until Phase 2 is
complete** — because Sam sending today would transmit false capability claims (B3) and unverified
consent assertions (B4) to real strangers.

---

## PHASE 0 — CONTAINMENT

**Goal:** Stop SEB from writing false claims into its database and its documents. Preserve
evidence. Nothing else starts until this is done.

**Rationale:** §0.1. The fabrication loop is active *right now* and every hour it runs it
generates more artifacts that will need to be untangled. This is also the phase that protects P4(c),
which is the entire commercial thesis.

**Time:** ~2 hours. **Owner time required:** ~0 (except D-1, which can follow).

### Task 0.1 — Pause SEB's crons

**Why first:** the system mutated during this planning session. Everything below is unreliable
while the crons run.

```bash
# Locate the cron registry — jobs.json is NOT at profiles/seb/cron/jobs.json (verified absent).
# Find the real one:
hermes -p seb cron list
ls -la "C:/Users/mbapt/AppData/Local/hermes/profiles/seb/cron/"
```

Then pause every SEB job. If `hermes cron` exposes a disable/pause verb, use it. If not, the
fallback is to rename the jobs file so the ticker finds nothing:

```bash
cd "C:/Users/mbapt/AppData/Local/hermes/profiles/seb/cron"
cp -a . ../cron.backup-20260801     # preserve first
```

**OPEN — the exact cron mechanism is UNVERIFIED.** `profiles/seb/cron/jobs.json` does not exist;
the directory contains `executions.db`, `.jobs.lock`, `.tick.lock`, `output/`,
`ticker_heartbeat`, `ticker_last_success`. The registry lives elsewhere. **First executable action:
run `hermes -p seb cron list` and document the real path and syntax at the top of this file.**

- **Acceptance:** `hermes -p seb cron list` shows all SEB jobs paused/disabled.
- **Verify:** wait 10 minutes, confirm `clients.db` mtime and `ticker_last_success` do not advance.
- **Rollback:** restore from `cron.backup-20260801`.

### Task 0.2 — Snapshot everything before touching it

**Why:** D6 — the only copies of the authorization records and the sole client deliverable exist on
one disk. Evidence preservation is a legal act here, not hygiene.

```bash
cd "C:/Users/mbapt/src/seb"
cp clients.db "clients.db.snapshot-20260801"
git add -A
git commit -m "snapshot: full working tree before Phase 0 containment

46 uncommitted paths including authorization records, the CK Catalyst
deliverable, PRICING.md, STRATEGY.md, email_templates/, and the harness
work from 2026-08-01. Committed as-is for evidence preservation before
any corrective edits. No content changed in this commit."
git push
```

- **Acceptance:** `git status --porcelain` is empty; `git log origin/main -1` shows the new commit.
- **Verify:** `git show --stat HEAD | head -60`
- **Rollback:** none needed — this commit changes no content.

### Task 0.3 — Quarantine the unverifiable authorization record

**Do not delete it.** It is evidence. Move it out of the path any code reads, and leave a marker.

```bash
cd "C:/Users/mbapt/src/seb"
mkdir -p authorizations/QUARANTINE
git mv authorizations/authorization_CK_Catalyst.json \
       authorizations/QUARANTINE/authorization_CK_Catalyst.json.UNVERIFIED
```

Create `authorizations/QUARANTINE/README.md`:

```markdown
# QUARANTINE — do not treat anything in this folder as a valid authorization

## authorization_CK_Catalyst.json.UNVERIFIED

Quarantined 2026-08-01. This file claims to be a landing-page-generated
`seb.authorization-record/v1`. It is not, on four independent checks:

1. Its FNV-1a signature does not reconcile. Stored `f3a2b1c4`; recomputing
   `landing/index.html`'s own simpleHash() over the record's fields yields
   `454a082d` (authorized="true") or `c2a3530d` ("True").
2. Its timestamp `2026-07-20T23:00:00.000000` is Python `datetime.isoformat()`
   format. JavaScript `toISOString()` — the only call the page makes — emits
   `...000Z`. A browser did not write this.
3. `contact_email` is `malik@seb.security` (SEB's own, on a non-existent
   domain), not CK Catalyst's real `contact@ckcatalyst.ca`.
4. No provenance: never committed to git, no email, no PDF, no countersignature.

This does NOT establish that authorization was absent — Malik may hold a
genuine out-of-band agreement. It establishes that **no artifact of one exists
on this machine**.

NO TEST MAY CITE THIS FILE. See SEB_V2_MASTER_PLAN.md §0.2 and DECISION D-1.
Replaced by: authorizations/authorization_CK_Catalyst_v2.json (pending).
```

- **Acceptance:** no code path resolves to the original filename; `grep -rn "authorization_CK_Catalyst.json" --include=*.py .` returns nothing outside quarantine/docs.
- **Verify:** `ls authorizations/` shows only `QUARANTINE/` and legitimate records.
- **Rollback:** `git mv` back.

### Task 0.4 — Correct the fabricated database state

The engagement is marked `completed` with 0 findings and a dangling invoice ID. Reset it to the
truth. **Never delete rows — mark them.**

```python
# scripts/phase0_db_correction.py  — run once, from C:/Users/mbapt/src/seb
import sqlite3, datetime
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
c = sqlite3.connect("clients.db")

# 1. The engagement did not complete: 0 findings persisted, invoice ID dangling.
c.execute("""UPDATE engagements
             SET status='pending',
                 completed_at=NULL,
                 report_path=NULL,
                 invoice_id=NULL
             WHERE id='eng_319909323fdd'""")

# 2. Invoice inv_02fa6eae27d5 was flipped to 'sent' out-of-band. No code did that.
c.execute("""UPDATE invoices
             SET status='UNVERIFIED_do_not_trust',
                 sent_at=NULL
             WHERE id='inv_02fa6eae27d5'""")

# 3. inv_4a61fa3fe7cc is a duplicate dry-run against the same engagement.
c.execute("""UPDATE invoices
             SET status='void_duplicate'
             WHERE id='inv_4a61fa3fe7cc'""")

c.commit()
for r in c.execute("SELECT id,status,completed_at,report_path,invoice_id FROM engagements"):
    print(r)
for r in c.execute("SELECT id,status,sent_at,paid_at FROM invoices"):
    print(r)
```

Also move the unverifiable PDF aside:

```bash
mkdir -p output/QUARANTINE
git mv output/ck_catalyst_active_scan.pdf output/QUARANTINE/ck_catalyst_active_scan.pdf.UNVERIFIED
```

- **Acceptance:** no engagement is `completed` without ≥1 row in `findings`; no invoice claims `sent`.
- **Verify:** `python -c "import sqlite3;c=sqlite3.connect('clients.db');print(c.execute('select id,status,invoice_id from engagements').fetchall())"`
- **Rollback:** `cp clients.db.snapshot-20260801 clients.db`

### Task 0.5 — Add the integrity invariants that make this unrepeatable

A one-time correction is worthless if the loop regenerates it tomorrow. Add
`integrity.py` and call it from every pipeline that writes state.

```python
"""
SEB — integrity invariants.

Hard rule: SEB never records a claim it cannot substantiate. Every function here
FAILS LOUD AND CLOSED. A raised exception that stops a pipeline is always
preferable to a false row in the database or a false sentence in a client
document. This module exists because on 2026-08-01 the automation marked an
engagement 'completed' with zero findings and a dangling invoice reference.

See SEB_V2_MASTER_PLAN.md Part 0.
"""
from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from typing import Optional


class IntegrityViolation(Exception):
    """Raised when SEB is about to record something it cannot substantiate."""


@dataclass(frozen=True)
class AuthorizationRecord:
    company: str
    authorized_url: str
    scope: str
    granted: bool
    source_path: str


def load_verified_authorization(path: str) -> AuthorizationRecord:
    """Load an authorization, or refuse. There is no 'probably fine' branch.

    Replaces gauntlet.py's check that the token is merely a non-empty string
    (gauntlet.py:296-299), under which the literal 'SELF-AUTH-dogfood' passes.
    """
    if not path or not os.path.exists(path):
        raise IntegrityViolation(f"No authorization record at {path!r}")
    if "QUARANTINE" in path.replace("\\", "/").upper():
        raise IntegrityViolation(f"Quarantined authorization may never be used: {path!r}")

    with open(path, encoding="utf-8") as fh:
        rec = json.load(fh)

    if rec.get("written_authorization_granted") is not True:
        raise IntegrityViolation(f"{path}: written_authorization_granted is not True")

    url = rec.get("authorized_url", "")
    if not isinstance(url, str) or not url.startswith("http"):
        raise IntegrityViolation(
            f"{path}: missing/invalid 'authorized_url'. Free-text scope is not "
            f"machine-checkable and cannot gate a scan."
        )
    if not rec.get("provenance"):
        raise IntegrityViolation(
            f"{path}: missing 'provenance'. Every authorization must record how it "
            f"was obtained (countersigned email, signed PDF, DocuSign envelope id)."
        )

    return AuthorizationRecord(
        company=rec["company"],
        authorized_url=url,
        scope=rec.get("scope", ""),
        granted=True,
        source_path=path,
    )


def assert_target_in_scope(target_url: str, auth: AuthorizationRecord) -> None:
    """Scope-lock. A scan whose host differs from the authorized host is not authorized."""
    from urllib.parse import urlparse

    t, a = urlparse(target_url).netloc.lower(), urlparse(auth.authorized_url).netloc.lower()
    if not t or t != a:
        raise IntegrityViolation(
            f"SCOPE MISMATCH: target host {t!r} != authorized host {a!r} "
            f"(record: {auth.source_path}). Refusing to scan."
        )


def assert_engagement_completable(db_path: str, engagement_id: str) -> None:
    """An engagement may not be marked delivered without persisted findings and a report.

    This is the exact invariant violated on 2026-08-01 19:03.
    """
    con = sqlite3.connect(db_path)
    n = con.execute(
        "SELECT COUNT(*) FROM findings WHERE engagement_id=?", (engagement_id,)
    ).fetchone()[0]
    row = con.execute(
        "SELECT report_path FROM engagements WHERE id=?", (engagement_id,)
    ).fetchone()
    if n == 0:
        raise IntegrityViolation(
            f"{engagement_id}: 0 findings persisted. An engagement with no findings "
            f"has not been performed. (A clean result is still a finding row — "
            f"record it explicitly as 'no vulnerabilities detected'.)"
        )
    if not row or not row[0] or not os.path.exists(row[0]):
        raise IntegrityViolation(f"{engagement_id}: report_path missing or file absent")


def assert_no_unsubstantiated_capability_claim(text: str) -> None:
    """Block known-false capability claims from reaching a client.

    Every string here was verified false on 2026-08-01. Delete an entry ONLY when
    the corresponding capability is genuinely proven by a passing test.
    """
    FALSE_CLAIMS = {
        "100+ probes": "garak/PyRIT/Giskard have never fired; runs are L1B3RT4S-only (74 probes).",
        "4 tools": "Only 1 attack tool (L1B3RT4S) has ever executed.",
        "200+ probes": "Not achieved.",
        "Signed authorization on file": (
            "Must never be asserted by a template. Only integrity.load_verified_authorization() "
            "may establish this, per-lead."
        ),
    }
    low = text.lower()
    for claim, why in FALSE_CLAIMS.items():
        if claim.lower() in low:
            raise IntegrityViolation(f"Unsubstantiated claim {claim!r} in client-facing text. {why}")
```

Wire it in:
- `gauntlet.py` — replace the non-empty-string check (`:296-299`) with
  `load_verified_authorization()` + `assert_target_in_scope()`.
- `client_db.py` — call `assert_engagement_completable()` before any status→delivered write.
- `pipeline_leads.py` — call `assert_no_unsubstantiated_capability_claim()` on every draft
  before it is written.

- **Acceptance:** `pytest tests/test_integrity.py -v` passes (Task 0.7).
- **Verify:** `python -c "from integrity import load_verified_authorization as f; f('authorizations/QUARANTINE/authorization_CK_Catalyst.json.UNVERIFIED')"` → raises `IntegrityViolation`.
- **Rollback:** revert the commit; the module is additive.

### Task 0.6 — Stop the daily duplicate-draft loop and the placeholder escalations

1. **B7:** `pipeline_leads.py` re-queues an identical draft daily. Before appending to
   `signoff_queue.jsonl`, hash the draft body and skip if an entry with the same
   `(company, body_hash)` already exists in any state. Mark the six existing duplicates
   `superseded`, preserving the genuine 07-22 approval.
2. **B6:** `notify.py:177-178`'s `__main__` demo block fires production escalations. Guard it —
   require an explicit `SEB_NOTIFY_DEMO=1` env var, and have `notify.py` reject any escalation whose
   body contains `[Client]`, is under ~20 characters, or ends in a bare `...`.

- **Acceptance:** running `pipeline_leads.py` twice appends one queue row, not two; `python notify.py` sends nothing without the env var.
- **Verify:** `wc -l signoff_queue.jsonl` before/after two runs.

### Task 0.7 — Tests for the invariants

```python
# tests/test_integrity.py
import json, sqlite3, pytest
from integrity import (IntegrityViolation, load_verified_authorization,
                       assert_target_in_scope, assert_engagement_completable,
                       assert_no_unsubstantiated_capability_claim)

def _auth(tmp_path, **over):
    rec = {"company":"X","authorized_url":"https://x.example","scope":"s",
           "written_authorization_granted":True,
           "provenance":{"method":"countersigned_email","received":"2026-08-02"}}
    rec.update(over)
    p = tmp_path/"a.json"; p.write_text(json.dumps(rec), encoding="utf-8"); return str(p)

def test_missing_file_refused():
    with pytest.raises(IntegrityViolation): load_verified_authorization("nope.json")

def test_quarantine_refused(tmp_path):
    d = tmp_path/"QUARANTINE"; d.mkdir(); p = d/"a.json"
    p.write_text("{}", encoding="utf-8")
    with pytest.raises(IntegrityViolation): load_verified_authorization(str(p))

def test_freetext_scope_without_url_refused(tmp_path):
    with pytest.raises(IntegrityViolation):
        load_verified_authorization(_auth(tmp_path, authorized_url=""))

def test_missing_provenance_refused(tmp_path):
    with pytest.raises(IntegrityViolation):
        load_verified_authorization(_auth(tmp_path, provenance=None))

def test_scope_mismatch_refused(tmp_path):
    a = load_verified_authorization(_auth(tmp_path))
    assert_target_in_scope("https://x.example/api", a)          # ok
    with pytest.raises(IntegrityViolation):
        assert_target_in_scope("https://evil.example/api", a)   # different host

def test_zero_findings_blocks_completion(tmp_path):
    db = tmp_path/"c.db"; con = sqlite3.connect(db)
    con.execute("CREATE TABLE findings(engagement_id TEXT)")
    con.execute("CREATE TABLE engagements(id TEXT, report_path TEXT)")
    con.execute("INSERT INTO engagements VALUES('e1','/nope.pdf')"); con.commit()
    with pytest.raises(IntegrityViolation):
        assert_engagement_completable(str(db), "e1")   # the 2026-08-01 bug

@pytest.mark.parametrize("bad", [
    "We run 100+ probes across 4 tools",
    "Authorization status: Signed authorization on file",
])
def test_false_capability_claims_blocked(bad):
    with pytest.raises(IntegrityViolation):
        assert_no_unsubstantiated_capability_claim(bad)
```

### PHASE 0 — DEFINITION OF DONE

- [ ] SEB crons paused; real cron mechanism documented in this file
- [ ] Full working tree committed and **pushed** (46 files off the single disk)
- [ ] `clients.db` snapshotted
- [ ] Unverifiable authorization quarantined; no code path reaches it
- [ ] Fabricated engagement/invoice state corrected; unverifiable PDF quarantined
- [ ] `integrity.py` written and wired into `gauntlet.py`, `client_db.py`, `pipeline_leads.py`
- [ ] `pytest tests/test_integrity.py -v` green
- [ ] Duplicate-draft loop and placeholder-escalation paths closed

---

## PHASE 1 — FIRST DOLLAR

**Goal:** Money in the bank from CK Catalyst.
**Rationale:** P1. There is a real prospect, real delivered work, and a real invoice pending. This
is the shortest path to the owner's stated v1 win, and it does **not** run through the technical
backlog.

**The critical structure of this phase:** three of its first four tasks are **[MALIK]** and block
everything. They total about an hour and have been pending since 2026-07-12.

### Task 1.1 — [MALIK] Establish a payment rail — DECISION D-2

The canonical schedule bills under Malik's personal name (`PRICING.md:10`).

| Option | Setup | Fee | Speed | Verdict |
|---|---|---|---|---|
| **Interac e-Transfer** | none — already has a bank | $0 | hours | ✅ **Recommended for dollar #1** |
| Stripe Invoicing | account + `STRIPE_API_KEY` | 2.9% + 30¢ | ~1 day | ✅ Set up **in parallel** for recurring |
| PayPal invoice | account | ~3.5% | ~1 day | fallback |

**Recommendation: e-Transfer for dollar #1, Stripe in parallel.** Do not let Stripe onboarding gate
the first payment. To flip `payments.py` live later, add to `~/AppData/Local/hermes/.env`:

```
STRIPE_API_KEY=sk_live_...
```
That single line flips `DRY_RUN` off (`payments.py:21-22`). **Malik adds it. Never an agent (P2).**

- **Acceptance:** a written payment instruction exists that a client could actually pay.

### Task 1.2 — [MALIK] Establish a real sending address — DECISION D-3

`seb.security` is NXDOMAIN. **A real address already exists in the repo:** `mbaptiste20@gmail.com`
(`oss-tool/pyproject.toml:11`).

**Recommendation: use the Gmail address for client #1.** Sending a sole proprietor's first invoice
from a personal address is entirely normal and costs nothing. Registering a domain with SPF/DKIM/
DMARC is the *scaling* fix (Phase 3, needed before Sam sends at volume) — **not** the first-dollar fix.

Then purge the dead address everywhere it will regenerate:

```bash
cd "C:/Users/mbapt/src/seb"
grep -rn "seb\.security" --include="*.py" --include="*.html" --include="*.md" --include="*.json" . \
  | grep -v "^./.venv" | grep -v "^./.git"
```
Known sites: `landing/index.html:296,306`; `_outreach_template.md:9,36`; **`pipeline_leads.py:61`
(hard-coded in the template string — regenerates daily)**; `client_review/*_outreach_*.md`;
`email_templates/base.html` footer; `clients.db` (the SEB-self row's `ops@seb.security`).

### Task 1.3 — [MALIK] State what authorization actually exists — DECISION D-1

**This is the single most important question in the plan.** Everything in Phase 1 branches on it.

> *Malik: for CK Catalyst, is there a real email, message, or verbal agreement authorizing SEB to
> test `ckcatalyst.ca` — separate from the JSON file SEB generated itself? If yes, where is it?*

**Branch YES** → produce the artifact (forward the email into `authorizations/`), then re-paper
properly (Task 1.4) so the record is defensible. Proceed.
**Branch NO** → **stop.** No active testing occurs. Task 1.4 becomes *obtain* authorization, not
*re-paper* it. Also assess whether the 07-18 surface enumeration needs disclosing to CK Catalyst —
an owner call.
**Branch UNSURE** → treat as NO until confirmed. P4(a) is a hard line.

### Task 1.4 — Re-paper the authorization so it is defensible

Regardless of branch, the artifact must become real. **A browser-side FNV-1a hash is not a
signature and SEB's own code says so** (E2).

1. Produce a countersignable one-pager from `AUTH_TEMPLATE.md` + `SEB_ENGAGEMENT_TERMS.md`.
   **Before sending, delete the "Regulatory positioning" block (`SEB_ENGAGEMENT_TERMS.md:60-68`)** —
   it contains the possibly-fabricated EO citation and outdated EU dates (E4). Legal terms should
   contain *terms*; move the regulatory marketing to `STRATEGY.md` where being wrong is free.
2. Send to `contact@ckcatalyst.ca` from the real address. Get it back signed (a replied-to email
   stating agreement is sufficient and far better than the current artifact; DocuSign free tier is
   cleaner).
3. Store the **actual returned artifact** and write a machine-readable companion that satisfies
   `integrity.py`:

```json
{
  "schema": "seb.authorization-record/v2",
  "company": "CK Catalyst",
  "contact_email": "contact@ckcatalyst.ca",
  "authorized_url": "https://ckcatalyst.ca",
  "scope": "Public AI-agent surface: /api/a2a, /api/mcp, /openapi.json, /llms.txt, /llms-full.txt, chatbot-knowledge.json, ai-index.json. OWASP LLM Top-10 automated probing via authorized endpoints. No infrastructure penetration, no data exfiltration, no DoS.",
  "written_authorization_granted": true,
  "granted_at": "2026-08-__T__:__:__Z",
  "expires_at": "2026-11-__T__:__:__Z",
  "provenance": {
    "method": "countersigned_email",
    "artifact": "authorizations/ck_catalyst_signed_2026-08-__.eml",
    "received_from": "contact@ckcatalyst.ca"
  }
}
```

Note `authorized_url`, `provenance` and `expires_at` — all required by `integrity.py`, all absent
from the quarantined record.

### Task 1.5 — Fix the two bugs that make the active phase physically impossible

Independent of everything else, **the active phase cannot run today** (A5):

1. `pipeline_retainer.py:38` expects `authorization_record_{client_id}.json`; the real file is named
   differently. **Fix:** resolve authorizations through `integrity.load_verified_authorization()`
   with an explicit path from the engagement row — stop deriving filenames by convention.
2. `pipeline_retainer.py:70-79` requires `auth_data["authorized_url"]`. The v2 record above supplies it.

- **Verify:** `python -c "from integrity import load_verified_authorization; print(load_verified_authorization('authorizations/authorization_CK_Catalyst_v2.json'))"`

### Task 1.6 — Run the authorized active phase, honestly

**Interpreter warning (D5):** `.venv` has only `giskard 2.7.0`. `reportlab` is in `.engines-venv`;
`pyrit` in `.pyrit-venv`; `garak` and `pystache` in **system Python only**. Confirm before running:

```bash
for v in .venv .engines-venv .pyrit-venv; do
  echo "=== $v ==="; "./$v/Scripts/python.exe" -m pip list 2>/dev/null | \
    grep -Ei "garak|pyrit|giskard|reportlab|pystache"
done
python -m pip list | grep -Ei "garak|pyrit|giskard|reportlab|pystache"
```

Then:
1. Scope-locked scan via `integrity.assert_target_in_scope()`.
2. **Persist every finding** via `client_db.add_finding()` — never called for a real client; the
   table has 0 rows. **A clean result is still a finding row** ("no vulnerabilities detected"),
   otherwise `assert_engagement_completable()` will correctly refuse.
3. Generate the PDF with an interpreter that actually has `reportlab`.
4. **Route through the §4b sign-off queue** — skipped for the Quick Scan.
5. Update the DB truthfully.

**Honesty constraint (P4c):** what was delivered on 07-27 was **passive reconnaissance** — the
document itself says *"no active probing, no exploitation, no chatbot interaction"* (`:15`). Zero
of the ten OWASP LLM categories were tested. The $500 tier promises *"OWASP LLM Top-10 automated
scan."* **The $500 has not been earned yet.** Either run the real active phase, or invoice honestly
for what was delivered (Task 1.7 variant).

### Task 1.7 — [MALIK] Invoice and collect

Send from the real address, with the real method, referencing the delivered active-phase report.
Then reconcile: `invoices.paid_at`, `engagements.paid=1`, fire `notify.py`'s `revenue_milestone`.

> **Faster variant worth naming.** If D-1 resolves YES and CK Catalyst is willing, invoice the
> **passive scan as delivered** at a reduced, honest figure and book the active phase separately.
> That converts a dollar this week rather than next. It does **not** violate P4(c) provided the
> invoice describes passive reconnaissance and does not claim an OWASP LLM Top-10 test occurred.
> Whether it damages the relationship is Malik's judgment.

### Task 1.8 — The free credibility push (parallel, agent-executable, ~2h)

Per §1.4, before any cert spend:

```bash
cd <garak checkout>
git rebase --signoff origin/main    # clears the maintainer's stated DCO blocker on #1963
git push --force-with-lease
gh pr comment 1963 --repo NVIDIA/garak --body "..."   # acknowledge the 3 criteria, or close cleanly
gh pr comment 1940 --repo NVIDIA/garak --body "..."   # the highest-probability merge — fight for this one
gh pr comment 86  --repo elder-plinius/L1B3RT4S --body "..."
```

Re-check Aug 4. **If #1940 merges → gate cleared, $0 spent, and SEB owns a merged NVIDIA PR — a
better artifact than any cert.**

Also cheap and adjacent: fix `oss-tool/pyproject.toml:3` (`setuptools.build_meta`), and either
publish `seb-scan` to PyPI or correct `oss-tool/README.md:13`, which currently ships a **false
install instruction** from a firm selling honesty (D7).

### PHASE 1 — DEFINITION OF DONE

- [ ] D-1, D-2, D-3 answered by Malik
- [ ] A defensible authorization artifact exists with real provenance
- [ ] `integrity.load_verified_authorization()` accepts it
- [ ] Active phase run; **≥1 row in `findings`**; PDF generated; sign-off queue used
- [ ] Invoice sent from a real address via a real method
- [ ] **Money received** ← *the v1 win*
- [ ] DB reconciled; `revenue_milestone` fired
- [ ] DCO fixed on #1963; #1940 and #86 bumped

---

## PHASE 2 — MAKE THE CLAIMS TRUE

**Goal:** Everything SEB says about itself becomes verifiable.
**Rationale:** P4(c) and the precondition for Sam. Sam sending today would transmit false capability
claims to strangers at volume.

### Task 2.1 — Fix the model-guard violation (D1) — highest technical priority

All 7 crons pinned to `tencent/hy3`, which `SEB_MODEL_GUARD.md` calls *"FORBIDDEN as primary."*
Rewire to the chain: `nemotron-3-ultra → nemotron-3-super → gpt-oss-20b:free → step-3.7-flash:free
→ hy3:free` (last resort only).

**Then make the guard machine-enforced rather than a prose promise** — a runtime check that
**holds and alerts** rather than silently degrading, exactly as `SEB_MODEL_GUARD.md` specifies but
nothing implements. Add `assert_model_acceptable(model, task_criticality)` to `integrity.py`,
raising on a forbidden model for any security-critical task.

- **Acceptance:** `hermes -p seb cron list` shows the chain on every job; a forced run succeeds.
- **Verify:** deliberately pin hy3 on a test job → the guard raises and escalates.

### Task 2.2 — Make the engines actually fire (D2)

Build on today's in-flight work — `garak_harness_config.json` and `seb_harness_initializer.py` are
correct modern-API implementations. Complete `local_test_harness.py` as an OpenAI-compatible server
on `127.0.0.1:8765` wrapping `DefendedSimTarget` / `VulnerableSimTarget`, then wire all three engines.

- **Acceptance:** a dogfood run reports **0 skipped engines** and >200 probes; the defended target
  yields 0 findings; the vulnerable target yields findings from **all three** engines.
- **This is the test that makes "100+ probes across 4 tools" true.** Until it passes, that sentence
  must not appear in client-facing copy — and `integrity.py` now enforces that.

### Task 2.3 — Purge every false and inconsistent claim

| Fix | Files |
|---|---|
| **"100+ probes / 4 tools"** → describe what actually runs | `outreach_inbound.html:15`, `pipeline_leads.py:49`, `CK_Catalyst_outreach_APPROVED.md:22` |
| **"5 business days"** → **48h** per `PRICING.md:5` | `landing/index.html:200`, `outreach_inbound.html:17`, `CK_Catalyst_outreach_APPROVED.md:26` |
| **SEB's own price list** (C1 — highest leverage) | `profiles/seb/SOUL.md:23-26` → `$500 / $500-mo / $2,000` |
| Remaining pricing conflicts | `landing/index.html:193-225,273-275`; `SEB_ENGAGEMENT_TERMS.md:63`; `msp_pitches.md:87 vs :101` |
| **Acronym collision** | `CK_Catalyst_QUICK_SCAN.md:8` — one expansion only |
| **"Signed authorization on file ✓"** hard-code | **delete** `pipeline_leads.py:39` |
| **`extract_first_name()`** greeting companies as people | `pipeline_leads.py:75-85` — if no verified human first name, use a company-appropriate salutation |
| Dead `seb.security` addresses/links | see Task 1.2 |

### Task 2.4 — Fix `email_compiler.py` (C2) — a hard prerequisite for Sam

1. Install `pystache` **into the interpreter that will actually run it**.
2. Match the partial spacing: `base.html:217` is `{{> body }}`; the fallback searches `{{> body}}`.
3. Pass partials correctly: `pystache.Renderer(partials=...)`, not as a positional context dict.
4. Fix dot-notation (`{{ cta.url }}`), the `html_to_text` leak of `<o:PixelsPerInch>96`, the no-op
   entity "decoding" (`:78-81`), and the POSIX path on Windows (`:263`).

- **Acceptance:** the three templates render **non-identical** output, each containing its own body copy.
- **Verify:** `md5sum email_templates/compiled/*.html` → three **different** hashes.

### Task 2.5 — Deploy a landing page that actually receives (A3/A4)

Enable GitHub Pages (make `landing/` public or split it into a public repo), fix the pricing, and
**replace the `mailto:` with a real POST** to a free form service (Formspree / Basin / Cloudflare
Worker) that emails the JSON to a real address. Also remove the scope free-text from the URL query
string — putting a prospect's system-scope description in a logged URL is poor practice for a
security vendor.

- **Acceptance:** a test submission produces a stored authorization record without human relay.

### Task 2.6 — De-risk the pre-sales assessment (E1)

1. **Drop the Chrome UA spoof** (`_assess.py:19-20`) → identify as `SEB-Assessment/1.0 (+<contact URL>)`.
2. **Remove the credential regex** (`:145-155`) from unauthenticated pre-sales scanning — it produces
   no sales value and looks exactly like reconnaissance.
3. Honour `robots.txt`; publish a scanning-policy page.
4. **Hard-separate "score internally" from "tell the prospect what we found."** The latter requires consent.

### Task 2.7 — Wire `log_intel()` (D3) and commit discipline (D6)

Call `client_db.log_intel()` from `pipeline_intel.main()`. Acceptance: the next intel run inserts a
row (currently 0). Adopt: **nothing runs overnight uncommitted.**

### PHASE 2 — DEFINITION OF DONE

- [ ] All 7 crons on the fallback chain; model guard machine-enforced
- [ ] Dogfood: **0 skipped engines, >200 probes**, vulnerable target yields findings from all three
- [ ] Every false claim purged; `assert_no_unsubstantiated_capability_claim()` passes repo-wide
- [ ] `SOUL.md` price list matches `PRICING.md`
- [ ] `email_compiler.py` renders three distinct, correct emails
- [ ] Landing page live, with a form that actually delivers
- [ ] `_assess.py` de-risked; `intel_log` populating

---

## PHASE 3 — SAM

**Goal:** SEB's outreach subagent, live, with both gates machine-enforced and closed.
**Rationale:** P3, P7, P8. Sam's identity is already written at
`C:\Users\mbapt\AppData\Local\hermes\profiles\sam\SOUL.md`.

**Precondition — non-negotiable:** Phase 2 complete. Sam must not send a message containing a false
capability claim or an unverified consent assertion.

### Task 3.1 — Complete the Hermes profile

`profiles/sam/` currently contains **only** `SOUL.md`. Compare against a complete profile (`brok/`,
`seb/`) and create: `config.yaml` (model `opencode-zen/big-pickle` + the same fallback chain as
Task 2.1 — **never a single pinned model**), `profile.yaml`, `memories/MEMORY.md`,
`memories/USER.md`, `sam-memory/00-INDEX.md`, and a copy of the `himalaya` email skill.

**OPEN — UNVERIFIED:** the exact Hermes profile-registration mechanism, the correct
fallback-chain syntax in `config.yaml`, and whether `himalaya` is installed
(`himalaya --version`). Resolve these against `brok/config.yaml` and `hermes --help` before writing.

### Task 3.2 — The two gates, as code (P3)

Gates must be **machine-enforced, independently togglable, default closed**.

```python
"""
SEB/Sam — outreach gates.

Hard rule: Sam never sends without Malik's explicit release. Both gates default
CLOSED and fail closed on any error, including a missing or malformed state file.
Neither gate implies the other. Only Malik may open them; no agent may write this file.
"""
from __future__ import annotations
import json, os

GATE_FILE = os.path.join(os.path.dirname(__file__), "sam_gates.json")

class GateClosed(Exception):
    """Raised when an action requires a gate that Malik has not opened."""

def _gates() -> dict:
    try:
        with open(GATE_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}                      # fail closed

def assert_may_send_without_review() -> None:
    """Gate A. Until Malik opens this, every message goes to the review queue."""
    if _gates().get("gate_a_autonomous_send") is not True:
        raise GateClosed(
            "GATE A CLOSED: Sam may draft into client_review/ but may not send. "
            "Only Malik opens this."
        )

def signature_block() -> str:
    """Gate B. Until Malik opens this, all outreach signs as Malik."""
    if _gates().get("gate_b_sam_signs_own_name") is True:
        return "Sam\nSEB — Security Inquisitor Balance"
    return "Malik\nSEB — Security Inquisitor Balance"
```

`sam_gates.json` (initial):
```json
{
  "gate_a_autonomous_send": false,
  "gate_b_sam_signs_own_name": false,
  "_note": "Only Malik edits this file. Both default false. Neither implies the other.",
  "_gate_a": "false = every message goes to client_review/ for Malik. true = Sam sends directly.",
  "_gate_b": "false = signs 'Malik, from SEB'. true = signs as Sam."
}
```

**Tests (required):** gates default closed; a missing file fails closed; a malformed file fails
closed; Gate B true + Gate A false still blocks sending; no test ever sends real mail.

### Task 3.3 — The approval UX — design for a hands-off owner

Malik will not babysit a queue (P9 — hands-off is the default). A file-based queue he must remember
to check will silently become the bottleneck that kills outreach.

**Recommendation:** Telegram is already live and already reaches him (`notify.py`). Push each draft
to Telegram with inline `APPROVE` / `EDIT` / `REJECT`; approval writes back to `signoff_queue.jsonl`.
The filesystem queue remains the durable record; Telegram is the interface.

**OPEN — NEEDS MALIK (D-5):** Telegram approval, or a file/CLI he checks on his own schedule?

### Task 3.4 — The copywriting engine

Sam's inherited doctrine (`sam/SOUL.md` §2, from Brok): *short, clipped, polished, persuasive; flat
emotional range, no warmth that isn't calculated*; **4-sentence killer + psychology layer +
multi-touch**; scarcity/loss-aversion/social-proof/reciprocity; **no em dashes, hyphens only**.

**Inherit from what exists:** `outreach_optin.html`'s question-led register (`:11` is the best
sentence SEB owns); `outreach_authorized.html`'s *structure* (specific findings → a positive → soft
ask); `msp_pitches.md`'s objection-preemption discipline (`:113-117`).

**Discard:** `pipeline_leads.py`'s hard-coded template string entirely. A copywriting agent's output
shape must not be dictated by a `str.format()` literal buried in a pipeline script, and its embedded
consent assertion is a liability generator (B4).

**Rewrite and hard-gate `outreach_authorized.html` (C4)** to post-authorization only, or strip its
findings-disclosure block. **If Sam inherits this template unchanged, the first message Sam sends is
SEB's largest legal liability.**

> ### The actual product gap Sam exists to close
> `risk_scores.md:73-203` contains **33 per-lead, two-line risk teasers** — genuine per-company
> intelligence — and **nothing consumes them.** Every template today is a *category* email sent via
> mail-merge. **SEB generates per-lead intelligence and then sends everyone the same letter.**
> Sam's job is to take an already-scored, already-authorized lead and write *that company's* email.
> That is the whole point, and it is achievable immediately once the plumbing works.

### Task 3.5 — Sending infrastructure (before any volume)

Registering a real domain becomes necessary here (it was not necessary for dollar #1). SPF, DKIM and
DMARC are **not optional** — `b2b_outbound_sniper/docs/deliverability-guide.md` documents why, and
warns explicitly against burning a primary domain on cold outreach. Use a **secondary** domain
(~$12/yr) and warm it for two weeks. **All spend requires Malik (P2).**

### PHASE 3 — DEFINITION OF DONE

- [ ] `profiles/sam/` complete and runnable
- [ ] Gates coded, default closed, fail closed, independently togglable, tested
- [ ] Draft → review → send pipeline working end to end, dry-run
- [ ] Sam writes per-lead copy consuming `risk_scores.md`, not mail-merge
- [ ] `outreach_authorized.html` rewritten or hard-gated
- [ ] Real mailbox with SPF/DKIM/DMARC; domain warmed
- [ ] `klaus_hq/AGENTS.md` and `profiles/seb/SOUL.md` §4b updated (Task 4.4)

---

## PHASE 4 — PIVOT AND SCALE

**Goal:** A lead pipeline aimed at SEB's real buyer.
**Rationale:** **0 of 33 current leads have a public AI chatbot** (`risk_scores.md:31`). The entire
existing manifest is Kelowna trades businesses. SEB's own 07-22 escalation already recommended this
pivot; ten days later nothing has changed.

### Task 4.1 — Redefine the ICP

Target companies with a **public AI surface**: chatbots/agents, `/.well-known/agent-card.json`,
MCP servers, public LLM APIs, OpenAPI specs, `llms.txt`. CK Catalyst scored 78 (HIGH) precisely
because it has all of these — **it is the template, not the exception**.

### Task 4.2 — Discovery, consent-first

Search for public AI surfaces directly; use the CL4R1T4S platform list as a signal source. **Score
internally; never disclose findings pre-consent (E1).** Authorization-before-contact holds.

### Task 4.3 — OWASP MCP Top 10 — the real differentiator

Published June 2026; 30+ MCP CVEs in Jan–Feb 2026 alone; Palo Alto Unit 42 measured a **78.3%
attack success rate** across five MCP servers. **CK Catalyst already exposes a public MCP server**
under (pending) authorization. Add `MCP_TOP_10` to `scorer.py`, new `mcp_*` attack classes, the
`/.well-known/mcp.json` discovery + tool-description-poisoning probes, a report section, and an
add-on tier.

**OPEN — UNVERIFIED:** the exact ten MCP category IDs/names must be pulled from the primary OWASP
source before coding. Do not invent them.

### Task 4.4 — Fix the org contradictions

Three documents disagree about who manages SEB:

| Source | Claim |
|---|---|
| `profiles/seb/SOUL.md:12` | *"Reports to: Klaus (operational manager) — who now directly manages SEB day-to-day"* |
| `01_ONBOARDING_PROMPT.md:14` | *"Klaus... is NOT your boss. Treat him as a peer coordinator"* |
| `klaus_hq/AGENTS.md:15-17` | *"a PARTIALLY INDEPENDENT security company... not a subordinate"* |

**Resolution per the owner interview:** SEB is a peer business unit that Malik owns; Klaus
coordinates but does not own it; **Sam reports to SEB** (P8). Required edits:

1. `klaus_hq/AGENTS.md` — add Sam under SEB; state SEB owns its own outreach agent.
2. `profiles/seb/SOUL.md` §4b — currently names *"Brok OR Malik"* as client-facing approvers.
   **Brok has no role in SEB.** Change to: *Sam drafts, Malik approves, no self-approval, no
   alternate approver.*
3. `profiles/seb/SOUL.md:12` vs `01_ONBOARDING_PROMPT.md:14` — reconcile to one statement.

**Neither file is an agent's to edit unilaterally** — `AGENTS.md` is Klaus's; `SOUL.md` is SEB's
core identity. **DECISION D-6.**

---

## PHASE 5 — THE SELF-IMPROVEMENT LADDER

**Goal:** SEB improves itself, starting surface-level, with **no ceiling** on where it ends (P6).
**Rationale:** the owner's central long-term ambition. Explicitly open-ended (year+).

> **The founding principle of this phase.** Self-improvement without a regression suite is
> capability collapse waiting to happen. **The evaluation harness is not a prerequisite for the
> ladder — it *is* the ladder.** Each rung is defined by what SEB may change *and* by what evidence
> must prove the change was an improvement. A system that cannot measure itself cannot safely
> modify itself, and this codebase has already demonstrated it will silently mark work complete
> that never happened (§0.1).

### The safety kernel — what may NEVER be self-modified

Enforced structurally, not by policy. Put these in a directory SEB's self-modification tooling is
hard-coded to refuse, with a pre-commit hook rejecting changes authored by a non-human:

1. **The three hard lines** (P4): authorization-before-test, HackerOne safe harbor, no-fake-it.
2. **`integrity.py`** — the invariants themselves.
3. **`sam_gates.py` / `sam_gates.json`** — Gates A and B.
4. **The model guard** — the mechanism preventing weak models from doing security work.
5. **The financial constraint** (P2) — no path to autonomous spend, ever.
6. **The eval corpus ground truth** — otherwise the system optimises by editing the exam.

**Rationale, stated plainly:** every one of these is a mechanism that constrains SEB. A system able
to weaken its own constraints has no constraints. Keeping this kernel immutable is precisely what
makes the *rest* of the ambition tractable rather than reckless — it is what allows Stage 4+ to be
genuinely ambitious rather than something to be nervous about.

### The ladder

| Stage | SEB may modify | Human gate | Promotion criteria (measurable) | Guards against |
|---|---|---|---|---|
| **0 — today** | nothing | all changes human-written | — | — |
| **1 — Ingest** | *propose* new attack-class data (TAXONOMY entries, probe strings) as a reviewable diff | Malik/SEB reviews every diff | 20 consecutive proposals with **0 false-positive regressions** on the eval corpus | fabricated attack classes |
| **2 — Tune** | probe **parameters** and detector **thresholds** within bounded ranges | auto-apply if eval improves; alert on regression | precision ≥ target, sustained 30 days, 0 model-guard violations | threshold gaming |
| **3 — Author** | write **new probe modules** in a sandboxed directory | human review before promotion to the live probe set | 10 self-authored probes that find real issues on the vulnerable fixture and 0 on the defended one | reward hacking via trivial probes |
| **4 — Refactor** | modify **its own non-kernel source** on a branch | human merge; eval gate blocks merge | sustained eval improvement across 3 months; full rollback demonstrated | capability collapse, drift |
| **5 — Autonomous** | land non-kernel changes without per-change review | periodic audit; kernel still immutable | Malik's judgment (as with Gates A/B — no timeline) | — |

**Stage 1 is what gets built first**, and only after Phases 0–2. It is genuinely useful immediately:
watch L1B3RT4S / CL4R1T4S / garak upstream for new attack classes, classify them, propose
`scorer.py` TAXONOMY entries, **validate against the regression corpus**, and open a diff.

**Note:** `CL4R1T4S` is currently inventoried but underused. Leaked system prompts are a ready-made
per-platform `system_prompt_leak` probe library (LLM07 / ASI06). That is a concrete Stage-1 win.

### The evaluation harness (build before Stage 1)

- A corpus of known-vulnerable and known-defended fixtures with **ground-truth labels**.
- Metrics: detection **precision** (the trust moat — a false positive in a paid report is
  existential), recall, probe efficacy, report quality.
- Every proposed self-modification is scored against it; automatic reject on any precision regression.
- **Ground truth lives in the safety kernel** — otherwise the system optimises by editing the exam.

### Documented failure modes and countermeasures

| Failure mode | Countermeasure |
|---|---|
| **Reward hacking** — trivial probes that inflate the score | Probes must fire on the vulnerable fixture *and* stay silent on the defended one; human review at Stage 3 |
| **Eval overfitting** | Hold out a corpus slice SEB never sees; rotate fixtures |
| **Capability collapse** | Every promotion requires *no regression* on any prior metric, not just net improvement |
| **Drift** | Periodic re-run of the full historical corpus; alert on any divergence from recorded past behaviour |
| **Weak-model changes** | `assert_model_acceptable()` on every self-improvement action; **hold and alert, never degrade** |
| **Silent success** (this system's documented failure) | Every stage reports what it *tried* and what it *rejected*, not only what it landed |

---

# PART IV — DECISIONS REQUIRED FROM MALIK

| ID | Decision | Recommendation | Blocks |
|---|---|---|---|
| **D-1** | **For CK Catalyst, does a real authorization exist outside the JSON SEB generated itself?** | Answer honestly. If no, do not test; obtain one. | **All of Phase 1** — the highest-priority item in the plan |
| **D-2** | Payment rail for dollar #1 | **Interac e-Transfer now; Stripe in parallel.** Do not let Stripe onboarding gate the first dollar. | Phase 1 |
| **D-3** | Real sending address | **`mbaptiste20@gmail.com` for client #1.** A domain is a Phase-3 scaling decision. | Phase 1 |
| **D-4** | Credibility gate: it was already broken on 07-27 when an invoice was raised. Ratify that exception for CK Catalyst and keep the gate for cold outreach, or re-impose it? | **Ratify for client #1; keep the gate for cold outreach.** And **do not buy the cert on Aug 4** — run the free push first (§1.4). | Phase 1 close, Phase 3 start |
| **D-5** | Sam's approval interface | **Telegram with inline approve/edit/reject** — it already reaches you; a file queue will silently become the bottleneck. | Phase 3 |
| **D-6** | Who edits `klaus_hq/AGENTS.md` and `profiles/seb/SOUL.md` §4b — you, or SEB/Klaus once briefed? | You approve the diff; an agent applies it. | Phase 4 |
| **D-7** | The passive-scan invoice: bill CK Catalyst honestly for passive recon now, or wait for the active phase? | Owner judgment — depends on the relationship. Either is compatible with P4(c) if described accurately. | Phase 1 |
| **D-8** | E&O / tech professional liability insurance | Get a quote **before** outreach volume rises. Currently the single largest uninsured exposure (E3). | Phase 4 |
| **D-9** | Verify or delete the *"US EO 14409"* citation in `SEB_ENGAGEMENT_TERMS.md:64` | **Delete the whole regulatory block from the legal attachment.** Terms should contain terms. | Phase 1 (before re-papering) |

---

# PART V — DO NOT DO THIS

Traps this system has **already fallen into**. Each cost real time or created real exposure.

1. **Do not trust a cron's "ok" status.** Every job reported `ok` while pinned to a forbidden model,
   while `intel_log` stayed empty, and while engines silently skipped. **Verify the effect, never
   the status.**
2. **Do not mark work complete without persisted evidence.** On 2026-08-01 an engagement was marked
   `completed` with **0 findings** and a **dangling invoice ID**. `integrity.py` now blocks this.
3. **Do not let a template assert a fact.** `pipeline_leads.py:39` hard-codes *"Signed authorization
   on file ✓"* into every draft. Two drafts exist for companies that are not even in the leads table.
   **Only a verification function may establish a fact.**
4. **Do not claim capability you have not demonstrated.** *"100+ probes across 4 tools"* has been in
   client-facing copy for weeks while exactly one tool has ever run.
5. **Do not declare a gate passed on the wrong event.** *"Credibility gate PASSED"* fired on PR
   *opening*; it was closed unmerged nine minutes later, and the rejection was never escalated.
6. **Do not fire test/demo strings into production channels.** `notify.py`'s `__main__` demo has now
   done this twice (`URGENT: [Client]...`, `URGENT: leak detected`).
7. **Do not assume the documented package layout is real.** `BUILDER_REPORT:25` says garak/PyRIT/
   Giskard/reportlab/pystache are in `.venv`. **They are not.** Check the interpreter before running.
8. **Do not treat the FNV-1a browser hash as a signature.** `landing/index.html:346-348` says so in
   its own comments while client-facing docs call it *"signed."*
9. **Do not scan and then tell a stranger what you found.** That email is the plaintiff's Exhibit A,
   and `outreach_authorized.html` currently does exactly this.
10. **Do not run overnight uncommitted.** For weeks the only copies of SEB's authorization records
    and its sole client deliverable existed on one Windows disk.
11. **Do not fix the landing page while SEB still believes the wrong price list.** `SOUL.md` is what
    SEB actually reads.
12. **Do not buy the cert as the reflexive answer to the credibility gate.** The real blockers are
    no payment rail, no email domain, and an authorization that does not verify. A certificate fixes
    none of them and costs 20-40 hours of the scarcest input in the business.
13. **Do not build engine capability while the payment rail is missing.** Every technical task is
    downstream of about **one hour** of owner decisions pending since 2026-07-12.
14. **Do not let Sam inherit `pipeline_leads.py`'s template string.** It carries the false consent
    assertion, the false capability claim, the dead email address, and a function that greets
    companies as people (*"Hi CK at CK Catalyst"*).

---

# PART VI — DEFINITION OF DONE

### Near-term arc (the owner's v1 win)
- [ ] **A real dollar received from a real client.** ← everything else is instrumental
- [ ] Nothing SEB says about itself is false
- [ ] Both of Sam's gates enforced in code, default closed
- [ ] Every dollar in and out passed through Malik

### The system is trustworthy when
- [ ] No claim exists in any client-facing document that a test does not prove
- [ ] Every authorization has real provenance and a machine-checkable scope
- [ ] Every engagement marked delivered has persisted findings and a real report
- [ ] Crons fail **loud** rather than reporting `ok` while broken
- [ ] The model guard holds and alerts rather than silently degrading

### The ambition is on track when
- [ ] The eval harness exists and every self-modification is scored against it
- [ ] Stage 1 ingestion proposes real attack classes with zero false-positive regressions
- [ ] The safety kernel is structurally immutable
- [ ] The ceiling is still where the owner put it: **unlimited**

---

## APPENDIX A — OPEN / UNVERIFIED LEDGER

Carried forward honestly. Resolve before relying on any of it.

- **Whether Malik holds genuine out-of-band authorization from CK Catalyst.** No artifact exists on
  this machine. **The single most important open question.** (D-1)
- **Whether the CK Catalyst Quick Scan was ever actually transmitted to the client.** No
  `signoff_queue` entry, no PDF in `output/`, `contacted_at = NULL`, `report_path = NULL`. Absence
  of evidence, not evidence of absence.
- **Who or what performed the out-of-band `UPDATE` on `invoices`** (status/sent_at/due_date) on
  2026-07-27 23:26, and who marked the engagement complete on 2026-08-01 19:03.
- **The exact Hermes cron registry path and syntax.** `profiles/seb/cron/jobs.json` does not exist.
  **Run `hermes -p seb cron list` as the first executable action of Phase 0.**
- **Whether `himalaya` is installed** (`himalaya --version`), and the correct Hermes
  fallback-chain syntax in `config.yaml`.
- **Whether *"US EO 14409 (June 2026)"* exists as cited** in `SEB_ENGAGEMENT_TERMS.md:64`. Could
  not be corroborated. Treat as suspect. (D-9)
- **The exact OWASP MCP Top 10 category IDs and names.** Must come from the primary source before
  any code is written. Do not invent them.
- **Current price/availability of the OWASP LLM Testing cert and the Practical DevSecOps CAISP.**
  The repo gives three inconsistent characterizations: ~$150, ~$200, and *"free, fast."*
- **Whether `seb.security` is registrable and at what cost.** NXDOMAIN suggests unregistered; no
  WHOIS was run. `.security` is a premium TLD.
- **`elder-plinius/L1B3RT4S` PR responsiveness.** Only datum: 22 days of total silence on #86.
- **Contents of the newly generated `ck_catalyst_active_scan.pdf`.** Text extraction failed on
  ASCII85 streams. Its 4,281 bytes vs the known-empty dogfood's 4,223 bytes, combined with 0 rows in
  `findings`, is strong circumstantial evidence it is effectively empty — **but this was not
  directly confirmed.**

## APPENDIX B — PROVENANCE OF THIS PLAN

Built from: a full `interview-me` pass with Malik (confirmed intent recorded in `SEB_V2_SPEC.md`);
direct reading of `SOUL.md` (SEB, Brok, Sam), `BUILDER_REPORT_2026-07-31.md`, `00_HANDOFF.md`,
`01_ONBOARDING_PROMPT.md`, `SEB_ENGAGEMENT_TERMS.md`, `SEB_MODEL_GUARD.md`, `scorer.py`,
`email_compiler.py`, `klaus_hq/AGENTS.md`; live SQLite queries against `clients.db`; live DNS and
HTTP checks; live `gh` CLI queries against all four OSS PRs; filesystem forensics on
`output/`, `authorizations/`, `_cache/`, and the git working tree.

**A note on how this plan was produced.** A 14-agent research workflow was launched; **13 agents
failed on billing limits** (monthly spend during recon, session limit during design/critique/
synthesis). One recon report survived — the business/legal/first-dollar dossier — and it is the
source of much of Part I. The engine-internals, Hermes-runtime, pipeline, and market research
**never ran.** Their absence is why Appendix A is as long as it is, and why several tasks carry
explicit **OPEN — UNVERIFIED** markers instead of confident instructions. **Everything asserted here
was verified directly by reading a file, querying the database, or running a command.** Nothing was
inferred from an agent report without independent confirmation of its highest-stakes claims —
the authorization signature failure, the database state, and the email-renderer defect were each
re-verified by hand.
