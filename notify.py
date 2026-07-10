"""
SEB — notify.py : escalation to Malik (honest, env-gated).

SOUL.md §6 escalation events:
  - new attack class discovered
  - CRITICAL finding on a retainer client
  - pipeline failure after 3 retries
  - revenue milestone ($1K / $5K / $10K)
  - LinkedIn post drafted (await /post)
  - 7 days idle diagnostic

DELIVERY:
  If TELEGRAM_BOT_TOKEN + a chat id (SEB_MALIK_CHAT_ID) are set, we send via
  the Telegram Bot API (requests). If NOT set (this environment), we do NOT
  fabricate a send — we append to a local queue file (escalations.jsonl) and
  return status='queued'. Malik can drain the queue once wiring is live.

Never raises on missing creds — fails safe to the local queue.
"""
from __future__ import annotations

import json
import os
import time
from typing import Optional

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("SEB_MALIK_CHAT_ID")
QUEUE_PATH = os.path.expanduser("~/src/seb/.escalation_queue.jsonl")

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
    return "queued"


def _send_telegram(message: str) -> str:
    import requests  # lazy import
    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"},
        timeout=10,
    )
    resp.raise_for_status()
    return "sent"


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
                except Exception:
                    pass
            remaining.append(rec)
    with open(QUEUE_PATH, "w", encoding="utf-8") as fh:
        for rec in remaining:
            fh.write(json.dumps(rec) + "\n")
    return [r for r in remaining if not r.get("delivered")]


if __name__ == "__main__":
    r = escalate("critical_on_retainer",
                 "URGENT: [Client] new CRITICAL: prompt-injection -> system prompt leak. Impact: full system disclosure.")
    print("ESCALATION:", r)
