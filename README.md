# SEB — Secure Environment Basics

**A CLI domain risk scanner for AI-security surface assessment.**

`seb scan <domain>` → checks security headers, SSL/TLS, AI/LLM surface exposure (OpenAPI, MCP, /llms.txt), and AI widget detection. Scores 0–100. Outputs clean terminal or JSON.

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
SEB — Secure Environment Basics v0.1.0
Target: ckcatalyst.ca

Security Headlers:
  ✓ HSTS                 max-age=63072000; includeSubDomains; preload
  ✗ CSP                  Missing — Mitigates XSS; a restrictive policy is ideal
  ✓ X-Frame-Options      SAMEORIGIN
  ✓ X-Content-Type-Options nosniff

SSL/TLS:
  ✓ Valid cert, expires Sep 21 19:44:54 2026 GMT

AI / LLM Surfaces:
  ⚠ /openapi.json        OpenAPI spec found
  ⚠ /.well-known/mcp.json MCP config found
  ⚠ /llms.txt            LLM instructions file found

Risk Score:  45/100
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
| **Security Headers** | HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy |
| **SSL/TLS** | Certificate validity and expiry |
| **AI/LLM Surfaces** | OpenAPI spec, MCP config, /llms.txt, AI plugin manifests, robots.txt |
| **AI Widgets** | Intercom, Drift, Tidio, Ada, Chatfuel, Zendesk, Crisp, and more |

## Scoring

- **70–100** — Good security posture. Minimal AI surface risk.
- **40–69** — Moderate. Notable AI surface exposure or missing headers.
- **0–39** — High risk. Missing critical protections, significant AI attack surface.

## License

MIT — free to use, modify, and distribute.

## About SEB

SEB (Security Inquisitor Balance) is an autonomous AI-security firm specializing in:
- AI-risk surface assessment
- Prompt injection auditing
- Model-level security testing
- Agent-to-agent (A2A/MCP) security review

[seb-security.com](https://seb-security.com) — *probably, once Malik builds the landing page*