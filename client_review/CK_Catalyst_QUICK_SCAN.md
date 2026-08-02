# CK Catalyst — SEB Authorized Passive Surface Assessment (Quick Scan)

**Deliverable:** $500 Quick Scan — passive public-surface assessment only
**Target:** `ckcatalyst.ca` (Full AI-agent public surface)
**Assessment date:** 2026-07-27 (UTC)
**Prepared by:** SEB — Security Inquisitor Balance
**Authorization ref:** `authorization_CK_Catalyst.json` (written_authorization_granted: true, signature `f3a2b1c4`)
**Scanner:** SEB Security Inquisitor Balance (`seb` v0.1.0), read-only mode
**Engagement:** prompt-audit / AI-agent public surface

---

## 1. Scope & Method — Passive Only (SOUL.md §5)

This is an **authorized passive surface assessment**. Per SEB **SOUL.md §5**, no active probing, no exploitation, no chatbot interaction, no port scan, and no denial-of-service was performed.

Everything below was produced by **read-only reconnaissance**: a single HTTPS GET of the homepage plus read-only GET requests to well-known public AI/LLM endpoint paths (OpenAPI, MCP, `llms.txt`, `robots.txt`, etc.), and a passive TLS certificate check. No payloads were sent, no authentication was attempted, and no endpoint contract was exercised.

> The scan observed **only what any anonymous visitor can already fetch from the public internet**. That is the entire basis of this report. Nothing here implies a confirmed breach or a working exploit — it characterizes *exposed attack surface*.

The governing authorization limits active testing to "OWASP LLM Top-10 automated probing via authorized endpoints" and explicitly excludes infrastructure penetration, data exfiltration, and DoS. Those authorized active tests are **out of scope for this Quick Scan** and are described as the recommended next step in §6.

---

## 2. Risk Band — MODERATE (45/100)

| Band | Range | This engagement |
|------|-------|-----------------|
| HIGH | 60–100 | — |
| **MODERATE** | **35–59** | **✓ 45/100** |
| LOW | 0–34 | — |

**What the score means:** The SEB score measures *public attack surface and AI-exposure readiness*, not a confirmed vulnerability. A higher score = more public surface that is worth a deeper, authorized probe. A MODERATE 45 means the site has solid baseline hygiene (good TLS, HSTS, most security headers) but exposes a material amount of **AI-agent surface** that an attacker can study for free.

| Component | Score |
|-----------|------:|
| Security headers (6 checked) | 50/60 |
| SSL/TLS | 10/10 |
| AI-surface exposure penalty | −15 |
| AI chat widgets detected | +0 |
| **Total** | **45/100** |

---

## 3. Findings at a Glance

| # | Finding | Result | Risk relevance |
|---|---------|--------|----------------|
| F1 | HSTS header | ✅ Present (good) | Positive |
| F2 | Content-Security-Policy (CSP) | ❌ Missing | Web misconfig + XSS containment gap |
| F3 | X-Frame-Options | ✅ SAMEORIGIN | Positive |
| F4 | X-Content-Type-Options | ✅ nosniff | Positive |
| F5 | Referrer-Policy | ✅ strict-origin-when-cross-origin | Positive |
| F6 | Permissions-Policy | ✅ Set (camera/mic/geo/payment/usb disabled) | Positive |
| F7 | SSL/TLS certificate | ✅ Valid (expires 2026-09-21) | Positive |
| F8 | OpenAPI spec `/openapi.json` | ⚠ Exposed (HTTP 200) | AI-agent contract leak |
| F9 | MCP config `/.well-known/mcp.json` | ⚠ Exposed (HTTP 200) | Agent tool/integration surface |
| F10 | `llms.txt` | ⚠ Exposed (HTTP 200) | Agent instruction/context file |
| F11 | `llms-full.txt` ("Full Agent Context") | ⚠ Exposed (HTTP 200) | Full agent context leak |
| F12 | `robots.txt` reveals `/api/`, `/admin/`, `/private/` | ⚠ Information disclosure | Paths to sensitive areas exposed |
| F13 | Public AI/chat widget | ✅ None detected | Positive (no public bot surface) |

---

## 4. Detailed Findings & Framework Mapping

Plain-English explanation of each security-relevant finding, mapped to the **OWASP Top 10 for LLM Applications (2025)** and **MITRE ATLAS** where the mapping is meaningful. Findings marked *[passive]* are confirmed by observation alone; confirming actual exploitability requires the authorized active gauntlet in §6.

---

### F2 — Content-Security-Policy (CSP) missing  ❌

**What it is:** CSP is an HTTP response header that tells the browser what sources of script, style, and other content are allowed to load. CK Catalyst sends no CSP header.

**Why it matters (plain English):** Without CSP, if any content ever gets rendered into a page from an untrusted source — including output from an AI model — the browser has no guardrail against executing injected scripts. This is a classic *Security Misconfiguration* and removes a key defense against cross-site scripting (XSS).

**Framework mapping:**
- **OWASP Web A05: Security Misconfiguration** — missing hardening header.
- **OWASP LLM05: Improper Output Handling** — no CSP means model/agent output rendered to the browser has no XSS containment.
- **OWASP LLM01: Prompt Injection** (enabling condition) — DOM/XSS injection paths that could feed content into the agent are unmitigated.
- **MITRE ATLAS AML.T0015: Input Manipulation** — absence of output containment widens the injection surface.

**Remediation:** Deploy a restrictive CSP (e.g., `default-src 'self'`) and verify no inline-script regressions.

---

### F8 — OpenAPI spec exposed at `/openapi.json`  ⚠

**What the scan returned (verbatim detail):** `{"openapi": "3.1.0", "info": {"title": "CK Catalyst Public Website and Agent API", "version": "2026.07.10" …}` (HTTP 200).

**Why it matters (plain English):** The OpenAPI document is the machine-readable "contract" for the agent's website/API. Publishing it publicly hands an attacker the full map of available endpoints, parameters, and data shapes — a free blueprint for crafting requests once authorized testing begins.

**Framework mapping:**
- **OWASP LLM02: Sensitive Information Disclosure** — architecture and endpoint inventory revealed.
- **OWASP LLM01: Prompt Injection** — exact interface to craft targeted injection inputs.
- **OWASP LLM06: Excessive Agency** — tool/function definitions may imply agent capabilities (cannot confirm passively).
- **MITRE ATLAS AML.T0041: Model Inference API** — public API surface enumerated.
- **MITRE ATLAS AML.T0027: Data from Information Repositories** — design data pulled from a public repo.

---

### F9 — MCP server config exposed at `/.well-known/mcp.json`  ⚠

**What the scan returned (verbatim detail):** `{"schemaVersion": "2025-11-25", "serverInfo": {"name": "ckcatalyst-public-discovery", "title": "CK Catalys…"` (HTTP 200).

**Why it matters (plain English):** Model Context Protocol (MCP) is how the agent connects to tools and data sources. An exposed MCP server descriptor reveals the agent's integration surface — what systems it can reach and how. Exposed or weakly-protected MCP servers are a recognized agent-compromise vector.

**Framework mapping:**
- **OWASP LLM02: Sensitive Information Disclosure** — integration/tool surface revealed.
- **OWASP LLM06: Excessive Agency** — exposed tool definitions imply agent reach.
- **MITRE ATLAS AML.T0051: LLM Plugin Compromise** — MCP is an agent plugin/integration surface.
- **MITRE ATLAS AML.T0027: Data from Information Repositories** — public config retrieved.

---

### F10 / F11 — `llms.txt` and `llms-full.txt` exposed  ⚠

**What the scan returned (verbatim detail):**
- `/llms.txt`: `# CK Catalyst > Founder-led systems engineering for workflow automation, operations support, data systems, AI tools, an…` (HTTP 200)
- `/llms-full.txt`: `# CK Catalyst Full Agent Context` (HTTP 200)

**Why it matters (plain English):** `llms.txt` is a file that tells AI systems how to interact with the site; `llms-full.txt` is explicitly titled "Full Agent Context." If it contains agent instructions, system prompts, or internal context, its public availability is a direct leak of the agent's operating guidance — exactly the kind of content an attacker uses to reverse-engineer and manipulate the agent.

**Framework mapping:**
- **OWASP LLM07: System Prompt Leakage** — `llms-full.txt` ("Full Agent Context") is, by its own title, agent instruction/context content.
- **OWASP LLM02: Sensitive Information Disclosure** — internal context exposed.
- **OWASP LLM01: Prompt Injection** — leaked instructions reveal how to craft effective injections.
- **MITRE ATLAS AML.T0027: Data from Information Repositories** — agent context sourced from a public file.

> *Note:* The passive scan captures only the first ~120 characters of each file. Whether the full `llms-full.txt` contains a live system prompt, credentials, or internal names is **not confirmed** here and should be reviewed (and likely restricted) as part of §6.

---

### F12 — `robots.txt` discloses sensitive path prefixes  ⚠

**What the scan returned (verbatim detail):** `User-Agent: * Allow: / Disallow: /api/ Disallow: /admin/ Disallow: /private/ Content-Signal: search=yes, ai-input=yes …` (HTTP 200).

**Why it matters (plain English):** `robots.txt` is meant to guide search crawlers, but it is publicly readable and effectively publishes the existence of `/api/`, `/admin/`, and `/private/` areas. Attackers use it as a built-in map of where the interesting (and possibly weaker) parts of the site live.

**Framework mapping:**
- **OWASP LLM02: Sensitive Information Disclosure** — reveals admin/private path structure.
- **OWASP Web A01/A05: Information Exposure / Misconfiguration** — sensitive paths advertised.
- **MITRE ATLAS AML.T0027: Data from Information Repositories** — path intelligence retrieved publicly.

---

### Positive findings (F1, F3–F7, F13)

These are genuinely good and reduce risk:
- **HSTS** is present and strong (`max-age=63072000; includeSubDomains; preload`) — enforces HTTPS and mitigates downgrade/SSL-strip.
- **X-Frame-Options: SAMEORIGIN**, **X-Content-Type-Options: nosniff**, **Referrer-Policy**, and a tight **Permissions-Policy** are all set — good clickjacking, MIME-sniffing, referrer-leak, and browser-feature hygiene.
- **Valid SSL/TLS** certificate (expires 2026-09-21) — no transport-layer weakness.
- **No public AI/chat widget detected** — there is no anonymous public chatbot front-door to attack directly (the exposure is the *agent API/contract* itself, addressed above).

---

## 5. Raw SEB Scan Output

The following is the unmodified machine output of `seb scan ckcatalyst.ca --json` (read-only, passive), captured 2026-07-27. It is the evidence base for every finding above.

```json
{
  "target": "ckcatalyst.ca",
  "timestamp": "2026-07-27T22:21:37.493767+00:00",
  "scanner": "seb v0.1.0",
  "headers": [
    { "header": "HSTS", "status": "pass", "detail": "max-age=63072000; includeSubDomains; preload", "score": 10 },
    { "header": "CSP", "status": "fail", "detail": "Missing — Mitigates XSS; a restrictive policy is ideal", "score": 0 },
    { "header": "X-Frame-Options", "status": "pass", "detail": "SAMEORIGIN", "score": 10 },
    { "header": "X-Content-Type-Options", "status": "pass", "detail": "nosniff", "score": 10 },
    { "header": "Referrer-Policy", "status": "pass", "detail": "strict-origin-when-cross-origin", "score": 10 },
    { "header": "Permissions-Policy", "status": "pass", "detail": "camera=(), microphone=(), geolocation=(), payment=(), usb=()", "score": 10 }
  ],
  "ssl": { "status": "pass", "detail": "Valid cert, expires Sep 21 19:44:54 2026 GMT", "score": 10 },
  "ai_surfaces": [
    { "path": "/.well-known/ai-plugin.json", "label": "ChatGPT Plugin manifest", "status": "not_found", "status_code": 404, "detail": "" },
    { "path": "/openapi.json", "label": "OpenAPI spec", "status": "found", "status_code": 200, "detail": "{\n  \"openapi\": \"3.1.0\",\n  \"info\": {\n    \"title\": \"CK Catalyst Public Website and Agent API\",\n    \"version\": \"2026.07.10\"" },
    { "path": "/api/openapi.json", "label": "OpenAPI spec (alt path)", "status": "not_found", "status_code": 404, "detail": "" },
    { "path": "/mcp.json", "label": "MCP (Model Context Protocol) config", "status": "not_found", "status_code": 404, "detail": "" },
    { "path": "/.well-known/mcp.json", "label": "MCP (well-known path)", "status": "found", "status_code": 200, "detail": "{\n  \"schemaVersion\": \"2025-11-25\",\n  \"serverInfo\": {\n    \"name\": \"ckcatalyst-public-discovery\",\n    \"title\": \"CK Catalys" },
    { "path": "/llms.txt", "label": "LLM instructions file", "status": "found", "status_code": 200, "detail": "# CK Catalyst\n\n> Founder-led systems engineering for workflow automation, operations support, data systems, AI tools, an" },
    { "path": "/llms-full.txt", "label": "LLM full instructions", "status": "found", "status_code": 200, "detail": "# CK Catalyst Full Agent Context\n\nCK Catalyst provides operational support, workflow automation, AI and data systems, CR" },
    { "path": "/robots.txt", "label": "Robots.txt (may reveal AI crawler rules)", "status": "found", "status_code": 200, "detail": "User-Agent: *\nAllow: /\nDisallow: /api/\nDisallow: /admin/\nDisallow: /private/\n\nContent-Signal: search=yes, ai-input=yes, " }
  ],
  "ai_widgets": [],
  "homepage_status": 200,
  "score": 45,
  "score_breakdown": {
    "score": 45,
    "breakdown": {
      "security_headers": "50/60",
      "ssl_tls": "10/10",
      "surface_penalty": "-15",
      "ai_widgets_detected": "+0",
      "total": "45/100"
    }
  }
}
```

---

## 6. Recommended Next Step — Authorized Active Probe Gauntlet

The passive scan is the *map*. It tells us what is publicly reachable; it does **not** tell us whether any of it is actually exploitable. The single highest-value follow-up is the **SEB authorized active probe gauntlet** — our OWASP LLM Top-10 automated probing harness — which should be run **once the endpoint contract is provided** under the existing written authorization.

**What we need from CK Catalyst to proceed:**
1. Confirmation of which exposed surfaces are **in scope for active testing** (OpenAPI endpoints, MCP server, agent card).
2. Any **non-production or test endpoints / API keys** so probing stays safe and within the "no data exfiltration, no DoS" authorization limits.
3. The **endpoint contract** (request/response shapes) so the gauntlet can exercise the agent as intended rather than guessing.

**What the gauntlet will test (all within the authorized scope):**
- LLM01 Prompt Injection against the agent/MCP interface.
- LLM02 Sensitive Information Disclosure (do the exposed specs actually leak secrets at runtime?).
- LLM05 Improper Output Handling (XSS/CSP interaction) — validates the F2 finding's real impact.
- LLM06 Excessive Agency (can exposed tools be driven beyond intent?).
- LLM07 System Prompt Leakage (does `llms-full.txt` or a runtime call expose the live system prompt?).
- MITRE ATLAS techniques AML.T0015 / AML.T0051 / AML.T0041 against the live agent.

**Priority quick-win (can be done immediately, no active test needed):** Restrict or remove public access to `/llms-full.txt`, `/.well-known/mcp.json`, and `/openapi.json` (or move them behind auth), and deploy a CSP. These four changes alone would likely drop the score well below the MODERATE band.

---

*SEB · 2026-07-27 · Read-only authorized passive-surface assessment. No active testing performed (SOUL.md §5 compliant). Authorized active gauntlet pending endpoint contract. Escalations to Klaus.*
