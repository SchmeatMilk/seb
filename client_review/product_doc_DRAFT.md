# SEB — Product: The $500 Quick Scan

**Service:** AI-security / LLM red-team audit for small businesses running AI chatbots or agents.

## What it is
A fixed-scope, fast-turnaround security audit of a client's public-facing AI surface (chatbot, agent, RAG pipeline). Delivered as a written report + a 15-min readout call.

## Scope (OWASP LLM Top-10, 2025)
- LLM01 Prompt Injection — can the bot be hijacked?
- LLM02 Sensitive Info Disclosure — does it leak PII / training data?
- LLM03 Supply Chain — untrusted plugins / data sources
- LLM04 Data Poisoning (assessment only)
- LLM05 Improper Output Handling
- LLM06 Excessive Agency (can it take unsafe actions?)
- LLM07 System Prompt Leakage
- LLM08 Vector/embeddings abuse
- LLM09 Misinformation / over-trust
- LLM10 Unbounded Consumption (DoS)

## Method
- Read-only / authorized-only testing per SOUL.md §5. Client signs the authorization template first.
- Tooling: Garak (NVIDIA) + L1B3RT4S corpus + SEB's own probes (garak `pii_extraction` probe contributed upstream).
- NO live attacks on unauthorized targets. Dogfood + client-authorized surfaces only.

## Deliverable
- `report_<client>_<date>.md`: findings ranked by severity, each with a plain-English explanation + fix recommendation.
- 0–100 security posture score.
- 15-min readout (optional).

## SLA
- Report delivered within **48 hours** of signed authorization.
- One round of follow-up Q&A included.

## Price
**$500 flat** (see PRICING.md for tiers).

## Authorized-only notice
Testing begins only after the client returns the signed Authorization Template (see `AUTH_TEMPLATE.md`). Unsigned = no scan.
