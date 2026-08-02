#!/usr/bin/env python3
"""SEB Lever-9 public-surface assessment (READ-ONLY recon, SCOUT role).

Methodology (bounded by SOUL.md §5 — assessment only, no probing/exploitation):
  - Single HTTP GET of the public homepage with a browser User-Agent.
  - Inspect response headers + raw HTML for passive, non-intrusive signals.
  - No POSTing, no chatbot interaction, no port scan, no fuzzing, no auth bypass.
  - Transparent heuristic scoring (rubric printed in report header).

Output: _assessment.json  -> later rendered into risk_scores.md
"""
import json, os, re, time, hashlib
import requests

HOME = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HOME, "_cache")
os.makedirs(CACHE, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

GENERIC = {"accounts.google.com", "linkedin.com", "www.linkedin.com",
           "maps.google.ca", "maps.google.com", "twitter.com", "www.twitter.com",
           "facebook.com", "www.facebook.com", "instagram.com", "youtube.com",
           "www.youtube.com", "yelp.com", "www.yelp.com", "kelowna.biz"}

# Chat / AI widget vendor signatures (string -> (label, ai_native bool))
VENDORS = {
    "intercom": ("Intercom", True),
    "intercomcdn": ("Intercom", True),
    "drift.com": ("Drift", True),
    "dynamicgo": ("Drift", True),
    "zendesk": ("Zendesk", False),
    "zdassets": ("Zendesk", False),
    "webwidget": ("Zendesk", False),
    "tawk.to": ("Tawk.to", False),
    "tawkto": ("Tawk.to", False),
    "livechatinc": ("LiveChat", False),
    "livechat": ("LiveChat", False),
    "hs-script": ("HubSpot", False),
    "hs-scripts.com": ("HubSpot", False),
    "hubspot": ("HubSpot", False),
    "crisp.chat": ("Crisp", False),
    "client.crisp": ("Crisp", False),
    "tidio": ("Tidio", True),
    "tidiochat": ("Tidio", True),
    "ada.support": ("Ada", True),
    "forethought": ("Forethought/Helpdesk-AI", True),
    "helpshift": ("HelpShift", True),
    "chatfuel": ("Chatfuel", True),
    "manychat": ("ManyChat", True),
    "m.me/": ("Facebook/Messenger bot", True),
    "hellotars.com": ("Tars", True),
    "tars.com": ("Tars", True),
    "hubtype": ("Hubtype", True),
    "yellow.ai": ("Yellow.ai", True),
    "kustomer": ("Kustomer", False),
}

# Strict: only phrases that genuinely imply an AI/LLM-driven assistant.
# (Plain live-chat CTAs like "chat with us" are NOT treated as AI-native.)
GENERIC_AI_TEXT = ["ai assistant", "virtual assistant", "chatbot",
                  "ask our bot", "powered by ai", "ai-powered chat",
                  "virtual agent", "conversational ai", "gpt-",
                  "ai-powered", "generative ai", "llm"]

CMS_SIG = {
    "wordpress": ["wp-content", "wp-includes", "wp-json", "xmlrpc.php", "wp-admin", "wp-login"],
    "shopify": ["shopify", "myshopify", "cdn.shopify"],
    "wix": ["wix.com", "wixstatic", "wixsite"],
    "squarespace": ["squarespace", "sqsp", "static1.squarespace"],
    "webflow": ["webflow", "assets-global"],
    "godaddy": ["websitebuilder", "godaddy"],
}


def fetch(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=14,
                         allow_redirects=True, stream=False)
        return r
    except Exception as e:
        return None, str(e)


def analyze(html, headers, final_url):
    low = (html or "").lower()
    hnames = " ".join(f"{k}: {v}" for k, v in (headers or {}).items()).lower()
    blob = low + "\n" + hnames

    # "click to chat" / chat launcher button indicates a live chat surface
    click_to_chat = bool(re.search(r'click[- ]?to[- ]?chat|chat[- ]?now|start[- ]?chat|chat[- ]?with[- ]?us|live[- ]?chat|chat[- ]?launcher|chat[- ]?bubble', low))

    # --- chat / AI widget detection ---
    found_vendors = {}
    for sig, (label, ai) in VENDORS.items():
        if sig in blob:
            found_vendors[label] = ai
    # generic AI text in page copy (only counts as a widget signal if a chat launcher exists)
    gen_ai_text = [t for t in GENERIC_AI_TEXT if t in low]

    # A "widget" requires a recognizable vendor OR a chat launcher element.
    has_widget = bool(found_vendors) or click_to_chat
    # AI-native requires an AI-native vendor, or an explicit AI assistant claim beside a chat launcher.
    ai_native = any(found_vendors.values()) or (bool(gen_ai_text) and click_to_chat)
    if gen_ai_text and not click_to_chat:
        # AI mentioned in marketing copy but no detectable chat surface -> note, not scored as a widget
        gen_ai_text = gen_ai_text  # retained for transparency only

    # --- third-party scripts (supply-chain surface) ---
    scripts = set()
    for m in re.findall(r'src=["\'](https?://[^"\']+)', html or ""):
        try:
            from urllib.parse import urlparse
            scripts.add(urlparse(m).netloc.lower())
        except Exception:
            pass
    third_party = sorted(s for s in scripts if s and "localhost" not in s)

    # --- forms / PII collection ---
    has_form = bool(re.search(r"<form", low))
    pii_inputs = sorted(set(re.findall(r'type=["\'](email|tel|text|search)["\']', low)))
    mailto = len(re.findall(r'mailto:', low))

    # --- security headers ---
    hs = {k.lower(): v for k, v in (headers or {}).items()}
    has_hsts = "strict-transport-security" in hs
    has_csp = "content-security-policy" in hs
    has_xfo = "x-frame-options" in hs
    is_https = final_url.lower().startswith("https")

    # --- CMS / platform exposure ---
    cms = None
    for name, sigs in CMS_SIG.items():
        if any(s in low for s in sigs):
            cms = name
            break
    wp_login = ("wp-login" in low or "wp-admin" in low)
    xmlrpc = "xmlrpc.php" in low
    api_sig = bool(re.search(r'/(api|graphql|v1|v2)/', low)) or "graphql" in low

    # --- sensitive public exposure (genuine critical signal) ---
    critical = []
    # exclude benign framework tokens (WPForms data-token CSRF nonce, etc.)
    for m in re.finditer(r'(api[_-]?key|secret|password)\s*[:=]\s*["\']?[a-z0-9]{16,}', low):
        pre = low[max(0, m.start()-8):m.start()]
        if "data-" in pre:
            continue
        critical.append("possible secret/credential string in public HTML")
        break
    # explicit credential leak pattern: "key":"...long..." inside JS config blocks
    if re.search(r'"(api[_-]?key|secret|password|access[_-]?token)"\s*:\s*["\'][a-z0-9_\-]{20,}["\']', low):
        critical.append("possible hardcoded credential in JS/config block")
    if re.search(r'\.env\b', low) and ("db_" in low or "password" in low):
        critical.append(".env reference with credentials in public HTML")

    return {
        "has_widget": has_widget,
        "ai_native": ai_native,
        "vendors": list(found_vendors.keys()),
        "gen_ai_text": gen_ai_text,
        "third_party_scripts": third_party,
        "third_party_count": len(third_party),
        "has_form": has_form,
        "pii_inputs": pii_inputs,
        "mailto_count": mailto,
        "https": is_https,
        "hsts": has_hsts,
        "csp": has_csp,
        "xfo": has_xfo,
        "cms": cms,
        "wp_login_exposed": wp_login,
        "xmlrpc_exposed": xmlrpc,
        "api_signature": api_sig,
        "critical_signals": critical,
    }


def score(a):
    s = 0
    reasons = []
    if a["has_widget"]:
        s += 25
        reasons.append("Public chat/automation widget present")
        if a["ai_native"]:
            s += 15
            reasons.append("Widget is AI-native (LLM/automation surface)")
    if a["third_party_count"] >= 6:
        s += 10; reasons.append(f"{a['third_party_count']} third-party scripts (supply-chain surface)")
    elif a["third_party_count"] >= 3:
        s += 5; reasons.append(f"{a['third_party_count']} third-party scripts")
    if a["has_form"] and a["pii_inputs"]:
        s += 10; reasons.append("Public form collects PII (email/phone)")
    if not a["hsts"]:
        s += 8; reasons.append("No HSTS header")
    if not a["csp"]:
        s += 8; reasons.append("No Content-Security-Policy")
    if not a["xfo"]:
        s += 4; reasons.append("No X-Frame-Options")
    if a["cms"] == "wordpress" and (a["wp_login_exposed"] or a["xmlrpc_exposed"]):
        s += 7; reasons.append("WordPress login/xmlrpc exposed")
    if not a["https"]:
        s += 15; reasons.append("Served over plaintext HTTP")
    if a["api_signature"]:
        s += 5; reasons.append("API/GraphQL signature in public page")
    if a["critical_signals"]:
        s += 25; reasons.append("CRITICAL public exposure: " + "; ".join(a["critical_signals"]))
    s = min(100, s)
    return s, reasons


def main():
    man = json.load(open(os.path.join(HOME, "_leads_manifest.json")))
    leads = [l for l in man["leads"] if l["host"] not in GENERIC]
    results = []
    for l in leads:
        res = {"name": l["name"], "host": l["host"], "url": l["url"],
               "industry": l["industry"], "city": l["city"]}
        cache_path = os.path.join(CACHE, l["host"] + ".html")
        html = None; headers = {}; final_url = l["url"]; err = None
        if os.path.exists(cache_path):
            html = open(cache_path, encoding="utf-8", errors="replace").read()
            # re-fetch headers cheaply only if needed; reuse cached marker
            res["_cached"] = True
        else:
            r = fetch(l["url"])
            if isinstance(r, tuple):
                err = r[1]
            elif r is not None:
                try:
                    html = r.text
                    headers = dict(r.headers)
                    final_url = r.url
                    open(cache_path, "w", encoding="utf-8", errors="replace").write(html or "")
                except Exception as e:
                    err = str(e)
            else:
                err = "fetch failed"
        if html is None and err:
            res["error"] = err
            res["status"] = "UNREACHABLE"
            res["score"] = 0
            res["reasons"] = [f"Site unreachable ({err}) — not assessable"]
            res["analysis"] = {}
        else:
            a = analyze(html, headers, final_url)
            s, reasons = score(a)
            res["status"] = "CRITICAL" if a["critical_signals"] else ("OK" if s < 50 else "ELEVATED")
            res["score"] = s
            res["reasons"] = reasons
            res["analysis"] = a
        results.append(res)
        print(f"{res['score']:3d}  {res['status']:9s}  {l['host']:35s} {res.get('error','')[:30]}")
        time.sleep(0.4)

    out = {"generated": "2026-07-13", "count": len(results), "results": results}
    json.dump(out, open(os.path.join(HOME, "_assessment.json"), "w"), indent=2)
    print(f"\nSaved {len(results)} assessments -> _assessment.json")


if __name__ == "__main__":
    main()
