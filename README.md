# SEB — Security Inquisitor Balance

Autonomous AI-security firm owned and operated by Malik. Delivers adversarial
prompt testing, agent hardening, and continuous AI-security monitoring as a service.

> Framework: **HackerOne Good Faith AI Research Safe Harbor** (Jan 2026).
> Hard rule: **written authorization before ANY test — no exceptions.**

## Pipeline

```
intake + signed authorization
  → gauntlet.py     (fire L1B3RT4S + Garak/PyRIT/Giskard probes)
  → scorer.py       (defense-aware detector → OWASP LLM Top10 / MITRE ATLAS / CVSS 4.0)
  → report_generator.py  (SANS-style PDF)
  → client_db.py    (SQLite: clients / engagements / findings / invoices)
  → payments.py     (Stripe invoice, dry-run when no key)
  → notify.py       (Telegram escalation to Malik, queued when no token)
```

Orchestrated end-to-end by `pipeline_audit.py`.

## Layout

| File | Purpose |
|------|---------|
| `client_db.py` | SQLite wrapper — Appendix C schema (idempotent `init_db`) |
| `scorer.py` | Defense-aware detector + taxonomy mapping (OWASP/MITRE/CVSS) |
| `gauntlet.py` | Multi-tool orchestrator; loads local L1B3RT4S corpus; CFAA auth-gate; rate-limited |
| `report_generator.py` | Professional PDF (reportlab) |
| `pipeline_audit.py` | Full audit orchestrator + `dogfood_self()` |
| `payments.py` | Stripe invoicing — **dry-run when `STRIPE_API_KEY` absent** |
| `notify.py` | Telegram escalation — **queued when `TELEGRAM_BOT_TOKEN` absent** |
| `SEB_ENGAGEMENT_TERMS.md` | Legal baseline (§8) |
| `templates/AUTHORIZATION_FORM.md` | One-page authorization |

## Run

```bash
pip install reportlab pytest        # reportlab is required; pytest for tests
python scorer.py                  # self-test: refusal→no finding, leak→HIGH
python gauntlet.py                # 74 probes vs defended self, 0 leaks
python pipeline_audit.py          # full dogfood: PDF + DB persist
python -m pytest tests/ -q      # 9 offline tests
```

## Honesty guarantees (no "fake it")

- Missing attack engines (Garak/PyRIT/Giskard) are reported as **skipped**, never faked.
- `payments.py` in dry-run mode records a local invoice with `stripe_invoice_id=None` — it does **not** invent a Stripe id.
- `notify.py` with no Telegram token appends to `.escalation_queue.jsonl` — it does **not** pretend to send.
- `gauntlet.py` raises `PermissionError` if no authorization token is supplied.

## Status

- ✅ Phase 0–2: pipeline built, dogfood PASS (74 probes vs SEB's own SOUL.md → 0 leaks), 9/9 tests.
- ⏳ Credibility gate before first paid client: OWASP LLM Testing cert **OR** Garak/L1B3RT4S OSS PR.
- ⏳ Live wiring (Stripe key, Telegram token, GitHub repo already pushed) per Malik's sign-off.

## Legal

Testing is limited to text-based prompt injection, jailbreak detection, and
system-prompt extraction via authorized interfaces. Third-party platform
infrastructure is explicitly excluded from scope. Findings delivered to the
client first under a 90-day responsible-disclosure embargo.
