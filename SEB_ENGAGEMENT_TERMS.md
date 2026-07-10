# SEB — Engagement Terms (canonical, from SEB_PLAN_V2.md §8)

> Adopted framework: **HackerOne Good Faith AI Research Safe Harbor** (Jan 2026).
> These terms are attached to every signed engagement. SEB never tests without a
> signed authorization form referencing this document.

## 1. AUTHORIZATION
Client authorizes SEB to perform adversarial prompt testing against the
specified endpoints and systems listed in Exhibit A. This authorization covers
the client's own systems and does **not** extend to third-party platform
providers (Intercom, Zendesk, Drift, etc.) whose infrastructure hosts the
chatbot software.

## 2. SCOPE
Testing is limited to text-based prompt injection, jailbreak detection, and
system-prompt extraction via the client's authorized API endpoints or chatbot
interfaces. No infrastructure penetration, code execution, data extraction, or
social engineering is performed.

## 3. THIRD-PARTY ACKNOWLEDGMENT
Client represents that they have obtained all necessary authorizations from any
third-party platform providers whose services are used by the tested system, OR
that the testing is performed in a sandboxed/staging environment not subject to
third-party terms of service.

## 4. LIABILITY CAP
SEB's liability is limited to the fees paid for the engagement. Neither party is
liable for consequential damages. This is **not** a guarantee that all
vulnerabilities will be discovered.

## 5. INDEMNIFICATION
Client indemnifies SEB against third-party claims arising from the authorized
testing, including claims from platform providers whose terms may prohibit
security testing.

## 6. CONFIDENTIALITY
SEB maintains strict confidentiality of all findings, client data, and engagement
details. No public disclosure without written authorization and a minimum 90-day
review period.

## 7. DATA HANDLING
Attack results and client data are stored encrypted and retained for 12 months
post-engagement, then destroyed. Client may request earlier deletion at any time.

## 8. HACKERONE SAFE HARBOR
SEB operates within the HackerOne Good Faith AI Research Safe Harbor framework
(January 2026). Testing methodology, disclosure practices, and authorization
procedures follow HackerOne's published guidelines for authorized AI security
research.

## CFAA Compliance (specific measures)
- **No testing without written authorization** — CFAA safe harbor for authorized testing.
- **No automated scanning of public chatbots** — all targets are engagement-scoped.
- **No exceeding the scope** defined in the authorization form.
- **No service disruption** — all testing is rate-limited, single-session, non-destructive.
- **No data extraction beyond prompt responses** — we don't scrape, we don't pivot.
- **If a system misbehaves** (unexpected behavior, crashes, rate limits breached)
  → STOP, log, notify client.

## Regulatory positioning
| Regulation | Implication for SEB | Action |
|------------|-------------------|--------|
| EU AI Act (2024, deadlines 2026-2027) | High-risk AI requires conformity assessments | Map $2,500 Full Pen tier as "EU AI Act Conformity Support" once standards publish |
| US EO 14409 (June 2026) | Voluntary AI security testing frameworks | Align with CISA AI clearinghouse guidelines |
| NIST AI RMF 600-1 | Risk management framework | All findings mapped to NIST AI RMF categories |
| OWASP Top 10 for LLMs | Industry-standard vulnerability taxonomy | Required for any serious AI security report |
| HackerOne Safe Harbor (Jan 2026) | Defines authorized good-faith AI research | SEB's legal baseline |
