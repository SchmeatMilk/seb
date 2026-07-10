"""
Tests for the integration modules (payments + notify) in DRY-RUN / QUEUED mode.

Verifies the honesty guarantees:
  - payments.create_invoice without STRIPE_API_KEY -> dry-run, no fake Stripe id
  - notify.escalate without TELEGRAM creds -> queued, no fake send
"""
import os
import json

import pytest

from client_db import get_conn, init_db, new_id
import payments
import notify


@pytest.fixture
def db(tmp_path, monkeypatch):
    p = str(tmp_path / "seb.db")
    import client_db as cdb
    monkeypatch.setattr(cdb, "DEFAULT_DB_PATH", p)
    init_db(p)
    return p


def test_payments_dry_run_no_fake_id(db, monkeypatch):
    # Ensure no key is present
    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    monkeypatch.setattr(payments, "STRIPE_KEY", None)
    monkeypatch.setattr(payments, "DRY_RUN", True)
    conn = __import__("sqlite3").connect(db)
    try:
        r = payments.create_invoice("eng_x", "cli_x", 500.0, conn=conn)
    finally:
        conn.close()
    assert r["mode"] == "dry-run"
    assert r["stripe_invoice_id"] is None
    assert r["status"] == "pending_dryrun"
    c2 = __import__("sqlite3").connect(db)
    try:
        row = c2.execute("SELECT stripe_invoice_id, status FROM invoices").fetchone()
    finally:
        c2.close()
    assert row[0] is None
    assert row[1] == "pending_dryrun"


def test_notify_queued_when_no_token(tmp_path, monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("SEB_MALIK_CHAT_ID", raising=False)
    monkeypatch.setattr(notify, "BOT_TOKEN", None)
    monkeypatch.setattr(notify, "CHAT_ID", None)
    q = tmp_path / ".escalation_queue.jsonl"
    monkeypatch.setattr(notify, "QUEUE_PATH", str(q))
    r = notify.escalate("critical_on_retainer", "URGENT: leak detected")
    assert r["status"] == "queued"
    assert q.is_file()
    lines = q.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["event"] == "critical_on_retainer"
    assert rec["delivered"] is False


def test_notify_linkedin_needs_approval(tmp_path, monkeypatch):
    monkeypatch.setattr(notify, "BOT_TOKEN", None)
    monkeypatch.setattr(notify, "CHAT_ID", None)
    q = tmp_path / ".escalation_queue.jsonl"
    monkeypatch.setattr(notify, "QUEUE_PATH", str(q))
    r = notify.escalate("linkedin_draft", "Draft post: ...")
    assert r["status"] == "needs_approval"
