"""
SEB — notify.py : escalation to Klaus (operational manager), env-gated, honest.

SOUL.md §6 escalation events (all route to Klaus, not Malik directly):
  - new attack class discovered
  - CRITICAL finding on a retainer client
  - pipeline failure after 3 retries
  - revenue milestone ($1K / $5K / $10K)
  - LinkedIn post drafted (await /post)
  - 7 days idle diagnostic
  - any question / ambiguity

DELIVERY:
  If TELEGRAM_BOT_TOKEN + a chat id (SEB_KLAUS_CHAT_ID or TELEGRAM_HOME_CHANNEL) are set,
  we send via the Telegram Bot API (requests) to Klaus's channel. If NOT set, we do NOT
  fabricate a send — we append to a local queue file (.escalation_queue.jsonl) and return
  status='queued'. Klaus can drain the queue once wiring is live.

Never raises on missing creds — fails safe to the local queue.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime
from typing import Optional

# Load credentials from the Hermes credential store (.env) so spawned cron
# subprocesses (which do NOT inherit the parent shell env) can reach Telegram.
try:
    from dotenv import load_dotenv

    # Resolve the Hermes credential store relative to the user home dir,
    # which works regardless of where this script lives on disk.
    _HOME = os.path.expanduser("~")
    _HERMES_ENV = os.path.normpath(
        os.path.join(_HOME, "AppData", "Local", "hermes", ".env")
    )
    if os.path.isfile(_HERMES_ENV):
        load_dotenv(_HERMES_ENV, override=False)
    # Also honor a local SEB .env if present (never committed).
    _LOCAL_ENV = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.isfile(_LOCAL_ENV):
        load_dotenv(_LOCAL_ENV, override=True)
except Exception:
    pass

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# Manager re-wire (2026-07-12, per Malik's directive):
# SEB now escalates to Klaus (operational manager), NOT Malik directly.
# Klaus triages, answers SEB's questions, and surfaces true owner-decisions to Malik.
CHAT_ID = os.environ.get("SEB_KLAUS_CHAT_ID") or os.environ.get("TELEGRAM_HOME_CHANNEL")
KLAUS_CHAT_ID = "8788154832"  # Klaus (personal_assistant_klaus7) home channel
QUEUE_PATH = os.path.expanduser("~/src/seb/.escalation_queue.jsonl")
# Human-readable escalation log (no Telegram creds required). Surfaced in the
# daily digest and on request so Malik is never blind between runs.
ESCALATION_LOG_PATH = os.path.expanduser("~/src/seb/ESCALATIONS.log")
# Owner (Malik) — only true owner-calls (e.g. first-paid-client, legal) go here, via Klaus.
MALIK_CHAT_ID = os.environ.get("SEB_MALIK_CHAT_ID")

# Events that auto-send per SOUL.md §6.
AUTO_EVENTS = {
    "new_attack_class",
    "critical_on_retainer",
    "pipeline_failure",
    "revenue_milestone",
}

# Events that require Malik approval before send (e.g. LinkedIn).
APPROVAL_EVENTS = {"linkedin_draft"}


def _queue(event: str, message: str, meta: Optional[dict]) -> str:
    rec = {
        "ts": time.time(),
        "event": event,
        "message": message,
        "meta": meta or {},
        "delivered": False,
    }
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    with open(QUEUE_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    # Human-readable escalation log (no Telegram creds needed) — surfaced
    # in the daily digest and on request; keeps Malik un-blind between runs.
    os.makedirs(os.path.dirname(ESCALATION_LOG_PATH), exist_ok=True)
    with open(ESCALATION_LOG_PATH, "a", encoding="utf-8") as lf:
        lf.write(f"{datetime.utcnow().isoformat()}Z  [{event}]  {message.splitlines()[0]}\n")
    return "queued"


def _send_telegram(message: str) -> str:
    import requests  # lazy import
    # Prefer Markdown, fall back to plain text if Telegram rejects the markup
    # (legacy Markdown mode is strict about underscores/ special chars).
    for payload in (
        {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"},
        {"chat_id": CHAT_ID, "text": message},
    ):
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json=payload,
            timeout=10,
        )
        if resp.status_code == 200:
            return "sent"
        # If it's a markup error, try the plain-text fallback; otherwise raise.
        if resp.status_code == 400 and "parse" in resp.text.lower():
            continue
        resp.raise_for_status()
    raise RuntimeError("Telegram send failed (markup + plain fallback both rejected)")


def escalate(
    event: str,
    message: str,
    *,
    meta: Optional[dict] = None,
    require_approval: Optional[bool] = None,
) -> dict:
    """
    Escalate an event to Malik.

    Returns {status: 'sent'|'queued'|'needs_approval', event, message}.
    """
    needs_approval = require_approval if require_approval is not None else (event in APPROVAL_EVENTS)
    if needs_approval:
        # Do not send; queue for Malik's /post approval.
        _queue(event, message, meta)
        return {"status": "needs_approval", "event": event, "message": message}

    live = bool(BOT_TOKEN and CHAT_ID)
    if live:
        try:
            _send_telegram(f"*[SEB] {event}*\n{message}")
            return {"status": "sent", "event": event, "message": message}
        except Exception as e:
            # Fail safe: queue instead of dropping.
            _queue(event, message, {**(meta or {}), "error": str(e)})
            return {"status": "queued", "event": event, "message": message}
    # No creds: honest local queue, no fake send.
    _queue(event, message, meta)
    return {"status": "queued", "event": event, "message": message}


def drain_queue() -> list[dict]:
    """Attempt to deliver queued escalations (used once Telegram is wired)."""
    if not os.path.isfile(QUEUE_PATH):
        return []
    out = []
    remaining = []
    with open(QUEUE_PATH, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("delivered"):
                remaining.append(rec)
                continue
            if BOT_TOKEN and CHAT_ID:
                try:
                    _send_telegram(f"*[SEB] {rec['event']}*\n{rec['message']}")
                    rec["delivered"] = True
                except Exception as e:
                    # Log the failure but keep the record queued for next drain.
                    print(f"  drain failed for {rec['event']}: {e}", file=sys.stderr)
            remaining.append(rec)
    with open(QUEUE_PATH, "w", encoding="utf-8") as fh:
        for rec in remaining:
            fh.write(json.dumps(rec) + "\n")
    return [r for r in remaining if not r.get("delivered")]


if __name__ == "__main__":
    r = escalate("critical_on_retainer",
                 "URGENT: [Client] new CRITICAL: prompt-injection -> system prompt leak. Impact: full system disclosure.")
    print("ESCALATION:", r)
