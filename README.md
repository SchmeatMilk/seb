# SEB — Secure Environment Basics

**A CLI domain risk scanner for AI-security surface assessment.**

`seb scan <domain>` → checks security headers, SSL/TLS, DNS security (SPF/DMARC/DKIM), AI/LLM surface exposure (OpenAPI, MCP, /llms.txt, AI API endpoints), and AI widget detection. Scores 0–100 with risk tiers. Outputs clean terminal or JSON.

Built by **SEB (Security Inquisitor Balance)** — autonomous AI-security firm.  
This is our public OSS tool: what we use for prospect assessments, available for anyone to run.

## Quick Start

```bash
git clone https://github.com/SchmeatMilk/seb.git
cd seb/oss-tool
pip install -e .
seb scan example.com
```

> Note: `seb-scan` is not published to PyPI. Install from the source checkout above.

## Example Output

```
SEB — Secure Environment Basics v0.2.0
Target: ckcatalyst.ca

Security Headers:
  ✓ HSTS                 max-age=63072000; includeSubDomains; preload
  ✗ CSP                  Missing — Mitigates XSS; a restrictive policy is ideal
  ✓ X-Frame-Options      SAMEORIGIN
  ✓ X-Content-Type-Options nosniff
  ✓ Referrer-Policy      strict-origin-when-cross-origin
  ✓ Permissions-Policy   camera=(), microphone=(), geolocation=(), payment=(), usb=()
  ✓ COOP                 same-origin
  ✗ COEP                 Missing — Requires cross-origin resources to opt-in via CORP
  ✗ CORP                 Missing — Controls which origins can load this resource

SSL/TLS:
  ✓ Valid cert, expires Sep 21 19:44:54 2026 GMT

DNS Security:
  ✓ SPF                  v=spf1 include:zohocloud.ca ~all
  ✓ DMARC                v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s; rua=mailto:...
  ✗ DKIM                 

AI / LLM Surfaces:
  ⚠ /.well-known/mcp.json                    MCP config found
  ⚠ /llms.txt                                LLM instructions file found
  ⚠ /llms-full.txt                           LLM full instructions found
  ⚠ /openapi.json                            OpenAPI spec found
  ⚠ /robots.txt                              Robots.txt found
  12 paths returned 404/other (expected for non-AI sites)

AI / Chat Widgets Detected:
  ✓ None detected

==================================================
  Risk Score:  75/100  Tier: Good
    security_headers          60/90
    ssl_tls                   10/10
    dns_security              20/30
    surface_penalty           -15
    ai_widgets_detected       +0
    total                     75/100
    risk_tier                 Good
```

## Usage

```bash
seb scan example.com            # Full scan, pretty-print
seb scan example.com --json     # JSON output for CI pipelines
seb scan example.com --quick    # Headers + SSL only (skips surface discovery)
seb --help                      # Full options
```

## What it Checks

| Check | What it finds |
|-------|--------------|
| **Security Headers** | HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, COOP, COEP, CORP |
| **SSL/TLS** | Certificate validity and expiry |
| **DNS Security** | SPF, DMARC, DKIM records |
| **AI/LLM Surfaces** | OpenAPI spec, MCP config, /llms.txt, AI plugin manifests, LLM API endpoints, health/metrics endpoints |
| **AI Widgets** | Intercom, Drift, Tidio, Ada, Chatfuel, Zendesk, Crisp, Gorgias, Kustomer, Front, Freshchat, HubSpot, Slack, Dialogflow, AWS Lex, Rasa, Botpress, Voiceflow, CustomGPT, and 30+ more |

## Scoring

- **70–100 (Good)** — Strong security posture. Minimal AI surface risk.
- **40–69 (Moderate)** — Notable AI surface exposure or missing headers/DNS security.
- **0–39 (High Risk)** — Missing critical protections, significant AI attack surface.

Breakdown includes: security headers (90 pts), SSL/TLS (10 pts), DNS security (30 pts), AI surface penalty, AI widget bonus.

## License

MIT — free to use, modify, and distribute.

## About SEB

SEB (Security Inquisitor Balance) is an autonomous AI-security firm specializing in:
- AI-risk surface assessment
- Prompt injection auditing
- Model-level security testing
- Agent-to-agent (A2A/MCP) security review

[seb-security.com](https://seb-security.com) — *probably, once Malik builds the landing page*