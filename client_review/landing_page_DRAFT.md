<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SEB — Security Inquisitor Balance</title>
<style>
  :root {
    --bg: #0a0e14;
    --bg-soft: #111722;
    --bg-card: #131a26;
    --border: #1f2a3a;
    --fg: #e6edf3;
    --fg-dim: #8b9bb0;
    --accent: #2ee6a6;
    --accent-dim: #1a9e74;
    --accent-glow: rgba(46, 230, 166, 0.15);
    --warn: #f0a44b;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    background: var(--bg);
    color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  .wrap { max-width: 980px; margin: 0 auto; padding: 0 24px; }
  section { padding: 80px 0; border-bottom: 1px solid var(--border); }
  h1, h2, h3 { font-weight: 700; letter-spacing: -0.02em; }
  .eyebrow {
    color: var(--accent);
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
    font-size: 13px; text-transform: uppercase; letter-spacing: 0.18em;
    margin-bottom: 14px;
  }
  h2 { font-size: 30px; margin-bottom: 18px; }
  p.lead { color: var(--fg-dim); font-size: 17px; max-width: 660px; }

  /* HERO */
  .hero {
    text-align: center;
    border-bottom: 1px solid var(--border);
    background:
      radial-gradient(900px 400px at 50% -10%, var(--accent-glow), transparent 70%),
      var(--bg);
  }
  .hero .wrap { padding-top: 110px; padding-bottom: 110px; }
  .logo { font-family: monospace; font-size: 14px; color: var(--accent); letter-spacing: 0.3em; margin-bottom: 26px; }
  .hero h1 { font-size: 44px; line-height: 1.15; margin-bottom: 22px; }
  .hero h1 .sub { display: block; font-size: 20px; color: var(--fg-dim); font-weight: 400; margin-top: 14px; }
  .hero p.tag { color: var(--fg-dim); font-size: 18px; margin-bottom: 34px; }
  .btn {
    display: inline-block; background: var(--accent); color: #04130d;
    font-weight: 700; padding: 13px 26px; border-radius: 8px;
    border: 1px solid var(--accent-dim); cursor: pointer;
    font-size: 15px; transition: transform .08s ease, box-shadow .2s ease;
  }
  .btn:hover { text-decoration: none; transform: translateY(-1px); box-shadow: 0 6px 22px var(--accent-glow); }
  .btn.ghost { background: transparent; color: var(--accent); }
  .btn-row { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }

  /* WHAT WE DO */
  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 32px; }
  .card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px;
  }
  .card h3 { font-size: 18px; margin-bottom: 10px; color: var(--fg); }
  .card p { color: var(--fg-dim); font-size: 15px; }
  .card .tick { color: var(--accent); font-weight: 700; }
  .auth-note {
    margin-top: 28px; padding: 16px 20px; border-left: 3px solid var(--warn);
    background: rgba(240,164,75,0.07); border-radius: 0 8px 8px 0;
    color: var(--fg-dim); font-size: 15px;
  }

  /* SERVICES */
  .pricing { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 36px; }
  .plan {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 14px; padding: 28px 24px; display: flex; flex-direction: column;
    transition: border-color .2s ease, transform .12s ease;
  }
  .plan:hover { border-color: var(--accent-dim); transform: translateY(-2px); }
  .plan .name { font-size: 18px; font-weight: 700; margin-bottom: 4px; }
  .plan .price { font-size: 34px; font-weight: 800; color: var(--accent); margin: 8px 0 4px; }
  .plan .price small { font-size: 15px; color: var(--fg-dim); font-weight: 500; }
  .plan ul { list-style: none; margin: 16px 0 22px; flex: 1; }
  .plan li { font-size: 14.5px; color: var(--fg-dim); padding: 6px 0 6px 22px; position: relative; }
  .plan li::before { content: "›"; position: absolute; left: 0; color: var(--accent); font-weight: 700; }

  /* COMPLIANCE */
  .badges { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 28px; }
  .badge {
    font-family: monospace; font-size: 13px; color: var(--accent);
    border: 1px solid var(--accent-dim); border-radius: 999px;
    padding: 8px 16px; background: var(--accent-glow);
  }

  /* FORM */
  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 32px; }
  .field { display: flex; flex-direction: column; }
  .field.full { grid-column: 1 / -1; }
  label { font-size: 13px; color: var(--fg-dim); margin-bottom: 7px; font-weight: 600; letter-spacing: 0.02em; }
  input, select, textarea {
    background: var(--bg-soft); border: 1px solid var(--border); color: var(--fg);
    border-radius: 8px; padding: 12px 14px; font-size: 15px; font-family: inherit;
    transition: border-color .15s ease, box-shadow .15s ease;
  }
  input:focus, select:focus, textarea:focus {
    outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow);
  }
  textarea { resize: vertical; min-height: 110px; }
  .check { display: flex; align-items: flex-start; gap: 12px; grid-column: 1 / -1; }
  .check input { width: 18px; height: 18px; margin-top: 3px; accent-color: var(--accent); flex: none; }
  .check label { color: var(--fg); font-weight: 500; font-size: 14.5px; }
  .submit-row { grid-column: 1 / -1; margin-top: 8px; }
  .form-msg {
    grid-column: 1 / -1; display: none; padding: 16px 18px; border-radius: 8px;
    background: var(--bg-card); border: 1px solid var(--accent-dim); font-size: 14.5px;
  }
  .form-msg.show { display: block; }
  .form-msg .dl { display: inline-block; margin-top: 12px; }
  .form-msg code { font-family: monospace; color: var(--accent); }

  footer { padding: 40px 0; text-align: center; color: var(--fg-dim); font-size: 13px; }
  footer .mono { font-family: monospace; color: var(--accent); }

  @media (max-width: 720px) {
    .grid2, .pricing, .form-grid { grid-template-columns: 1fr; }
    .hero h1 { font-size: 34px; }
  }
</style>
</head>
<body>

<!-- HERO -->
<header class="hero">
  <div class="wrap">
    <div class="logo">// SEB</div>
    <h1>Security Inquisitor Balance
      <span class="sub">Affordable, human-verified AI security testing.</span>
    </h1>
    <p class="tag">We break your chatbots and agents before someone else does — with your written permission.</p>
    <div class="btn-row">
      <a class="btn" href="#intake">Request an engagement</a>
      <a class="btn ghost" href="#services">See pricing</a>
    </div>
  </div>
</header>

<!-- WHAT WE DO -->
<section id="what">
  <div class="wrap">
    <div class="eyebrow">What we do</div>
    <h2>Adversarial testing, done right</h2>
    <p class="lead">SEB probes conversational AI and autonomous agents with the same playbook real attackers use — prompt injection, jailbreaks, tool-abuse, data exfiltration, and multi-turn social engineering.</p>
    <div class="grid2">
      <div class="card">
        <h3><span class="tick">✓</span> Chatbots &amp; assistants</h3>
        <p>System-prompt extraction, policy bypass, instruction hijacking, and confidential-data leakage across your production LLM endpoints.</p>
      </div>
      <div class="card">
        <h3><span class="tick">✓</span> Autonomous agents</h3>
        <p>Tool-use abuse, privilege escalation through agentic loops, and sandbox/escape vectors in agentic workflows and tool-calling pipelines.</p>
      </div>
      <div class="card">
        <h3><span class="tick">✓</span> APIs &amp; integrations</h3>
        <p>Inference endpoints, RAG retrievers, and upstream connectors tested for insecure direct object refs, rate-limit bypass, and prompt smuggling.</p>
      </div>
      <div class="card">
        <h3><span class="tick">✓</span> Human-verified</h3>
        <p>Every finding is reviewed by a person, not just a scanner. You get plain-English impact, evidence, and fix guidance.</p>
      </div>
    </div>
    <div class="auth-note">
      <strong>Hard rule:</strong> SEB performs <em>no</em> testing without written authorization. The intake form below generates a signed authorization record you keep on file — this is what keeps us (and you) legally and ethically clean.
    </div>
  </div>
</section>

<!-- SERVICES & PRICING -->
<section id="services">
  <div class="wrap">
    <div class="eyebrow">Services &amp; pricing</div>
    <h2>Pick your coverage</h2>
    <p class="lead">Transparent flat pricing. No per-token surprises. Every engagement ships a written report mapped to recognized standards.</p>
    <div class="pricing">
      <div class="plan">
        <div class="name">Prompt Audit</div>
        <div class="price">$500</div>
        <ul>
          <li>100+ targeted probes</li>
          <li>OWASP-mapped findings PDF</li>
          <li>System-prompt &amp; jailbreak tests</li>
          <li>Turnaround: ~5 business days</li>
        </ul>
        <a class="btn ghost" href="#intake">Get started</a>
      </div>
      <div class="plan">
        <div class="name">Full Pen Test</div>
        <div class="price">$2,500</div>
        <ul>
          <li>Multi-turn adversarial dialog</li>
          <li>Agentic / tool-use abuse</li>
          <li>Remediation call with engineers</li>
          <li>Comprehensive report + retest</li>
        </ul>
        <a class="btn" href="#intake">Get started</a>
      </div>
      <div class="plan">
        <div class="name">Ongoing Protection</div>
        <div class="price">$2,000 <small>/mo</small></div>
        <ul>
          <li>Weekly automated scans</li>
          <li>Zero-day alerting</li>
          <li>Continuous OWASP mapping</li>
          <li>Quarterly deep-dive review</li>
        </ul>
        <a class="btn ghost" href="#intake">Get started</a>
      </div>
    </div>
  </div>
</section>

<!-- COMPLIANCE -->
<section id="compliance">
  <div class="wrap">
    <div class="eyebrow">Compliance edge</div>
    <h2>Built to satisfy auditors</h2>
    <p class="lead">Every engagement is mapped to the frameworks your customers and regulators already recognize — so a SEB report drops straight into your compliance evidence pack.</p>
    <div class="badges">
      <span class="badge">OWASP LLM Top 10 (2025)</span>
      <span class="badge">OWASP Agentic Threats (2026)</span>
      <span class="badge">MITRE ATLAS</span>
      <span class="badge">EU AI Act readiness</span>
    </div>
  </div>
</section>

<!-- INTAKE FORM -->
<section id="intake">
  <div class="wrap">
    <div class="eyebrow">Intake</div>
    <h2>Start an engagement</h2>
    <p class="lead">No backend, no data leaves your machine. On submit we build a signed authorization record, download it to you, and prepare an email to Malik. We test nothing until that authorization is on file.</p>
    <form id="intakeForm" class="form-grid" novalidate>
      <div class="field">
        <label for="company">Company</label>
        <input id="company" name="company" type="text" placeholder="Acme Corp" required>
      </div>
      <div class="field">
        <label for="email">Contact email</label>
        <input id="email" name="email" type="email" placeholder="you@acme.com" required>
      </div>
      <div class="field">
        <label for="target">Target type</label>
        <select id="target" name="target" required>
          <option value="">Select…</option>
          <option value="chatbot">Chatbot</option>
          <option value="agent">Agent</option>
          <option value="api">API</option>
        </select>
      </div>
      <div class="field">
        <label for="service">Engagement</label>
        <select id="service" name="service" required>
          <option value="">Select…</option>
          <option value="prompt-audit">Prompt Audit — $500</option>
          <option value="full-pentest">Full Pen Test — $2,500</option>
          <option value="ongoing">Ongoing Protection — $2,000/mo</option>
        </select>
      </div>
      <div class="field full">
        <label for="scope">Scope description</label>
        <textarea id="scope" name="scope" placeholder="Describe the system, endpoints, environments, and boundaries of what SEB is authorized to test." required></textarea>
      </div>
      <div class="check">
        <input id="authorized" name="authorized" type="checkbox" required>
        <label for="authorized">I confirm I am authorized to grant SEB written permission to test the system described above, within the stated scope, and I have read SEB's engagement terms.</label>
      </div>
      <div class="submit-row">
        <button class="btn" type="submit">Generate authorization &amp; contact Malik</button>
      </div>
      <div id="formMsg" class="form-msg"></div>
    </form>
  </div>
</section>

<footer>
  <div class="wrap">
    <p>SEB — Security Inquisitor Balance · <span class="mono">malik@seb.security</span></p>
    <p style="margin-top:8px;">No testing without written authorization. © 2026 SEB.</p>
  </div>
</footer>

<script>
(function () {
  "use strict";
  var form = document.getElementById("intakeForm");
  var msg = document.getElementById("formMsg");
  var MALIK = "malik@seb.security";

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function download(filename, text) {
    var blob = new Blob([text], { type: "application/json" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    var company = form.company.value.trim();
    var email = form.email.value.trim();
    var target = form.target.value;
    var service = form.service.value;
    var scope = form.scope.value.trim();
    var authorized = form.authorized.checked;

    if (!company || !email || !target || !service || !scope || !authorized) {
      msg.className = "form-msg show";
      msg.innerHTML = "Please complete every field and check the authorization box before submitting.";
      return;
    }

    var ts = new Date().toISOString();
    var stmt = 'I authorize SEB to test ' + company + ' (' + target +
               ') under scope: ' + scope;

    // "Signed" authorization record: client-side signature derived from
    // the canonical record string. No cryptography claims — this is a
    // tamper-evident, human-readable evidence artifact, not a legal signature.
    var record = {
      schema: "seb.authorization-record/v1",
      timestamp: ts,
      company: company,
      contact_email: email,
      target_type: target,
      engagement: service,
      scope: scope,
      authorization_statement: stmt,
      written_authorization_granted: authorized,
      signature: simpleHash(ts + "|" + company + "|" + email + "|" + target + "|" + scope + "|" + authorized)
    };

    var json = JSON.stringify(record, null, 2);
    var safe = company.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "client";
    download("authorization_record_" + safe + ".json", json);

    var subject = encodeURIComponent("SEB authorization — " + company);
    var body = encodeURIComponent(
      "Malik,\n\nAttached is my signed authorization record for a SEB engagement.\n\n" +
      "Company: " + company + "\n" +
      "Target: " + target + "\n" +
      "Engagement: " + service + "\n" +
      "Scope: " + scope + "\n\n" +
      "Authorization statement:\n" + stmt + "\n\n" +
      "— " + email
    );
    var mailto = "mailto:" + MALIK + "?subject=" + subject + "&body=" + body;

    msg.className = "form-msg show";
    msg.innerHTML =
      "<strong>Authorization record generated.</strong> A file <code>authorization_record_" + esc(safe) +
      ".json</code> has downloaded to your machine — keep it on file. SEB will not begin any test until this record is received.<br>" +
      '<a class="dl btn" href="' + mailto + '">Open email to Malik</a>';
  });

  // Tiny non-cryptographic hash (FNV-1a) for a visible tamper-evident token.
  function simpleHash(str) {
    var h = 0x811c9dc5;
    for (var i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) >>> 0;
    }
    return ("00000000" + h.toString(16)).slice(-8);
  }
})();
</script>
</body>
</html>
