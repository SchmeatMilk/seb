"""
SEB — client/engagement/finding database wrapper.

SQLite backend. Schema is the canonical Appendix C schema from
SEB_PLAN_V2.md (clients, engagements, findings, intel_log, leads, invoices).

All writes are local. No network. CFAA-safe by construction: this module
never performs testing — it only records authorized engagement state.
"""
from __future__ import annotations

import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional

DEFAULT_DB_PATH = os.path.expanduser("~/src/seb/clients.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    company TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    tier TEXT DEFAULT 'free',
    status TEXT DEFAULT 'lead',
    source TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS engagements (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    target_urls TEXT NOT NULL,
    tier TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    authorization_file TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    report_path TEXT,
    invoice_id TEXT,
    amount REAL,
    paid BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagements(id),
    attack_class TEXT NOT NULL,
    owasp_id TEXT,
    mitre_atlas_id TEXT,
    cvss_score REAL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    evidence TEXT,
    impact TEXT,
    remediation TEXT,
    false_positive BOOLEAN DEFAULT 0,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS intel_log (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    commit_hash TEXT,
    new_attacks INTEGER DEFAULT 0,
    attacks_integrated INTEGER DEFAULT 0,
    novel_class BOOLEAN DEFAULT 0,
    run_time_ms INTEGER,
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    company TEXT,
    url TEXT,
    chatbot_platform TEXT,
    status TEXT DEFAULT 'identified',
    contacted_at TIMESTAMP,
    authorization_given BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoices (
    id TEXT PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagements(id),
    client_id TEXT NOT NULL REFERENCES clients(id),
    amount REAL NOT NULL,
    stripe_invoice_id TEXT,
    status TEXT DEFAULT 'pending',
    sent_at TIMESTAMP,
    paid_at TIMESTAMP,
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def get_conn(path: str | None = None) -> sqlite3.Connection:
    path = path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path: str | None = None) -> str:
    """Create the DB file and apply the full schema. Idempotent (IF NOT EXISTS)."""
    path = path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = get_conn(path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
    return path


def _touch_client(conn: sqlite3.Connection, client_id: str) -> None:
    conn.execute(
        "UPDATE clients SET updated_at = ? WHERE id = ?", (_now_iso(), client_id)
    )


def add_client(
    name: str,
    company: str,
    email: str,
    *,
    phone: Optional[str] = None,
    tier: str = "free",
    status: str = "lead",
    source: Optional[str] = None,
    notes: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
    client_id: Optional[str] = None,
) -> str:
    own = conn is None
    conn = conn or get_conn()
    cid = client_id or new_id("cli")
    try:
        conn.execute(
            """INSERT INTO clients (id, name, company, email, phone, tier, status, source, notes)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (cid, name, company, email, phone, tier, status, source, notes),
        )
        conn.commit()
    finally:
        if own:
            conn.close()
    return cid


def add_engagement(
    client_id: str,
    target_urls: list[str],
    tier: str,
    *,
    status: str = "pending",
    authorization_file: Optional[str] = None,
    amount: Optional[float] = None,
    engagement_id: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> str:
    own = conn is None
    conn = conn or get_conn()
    eid = engagement_id or new_id("eng")
    try:
        conn.execute(
            """INSERT INTO engagements (id, client_id, target_urls, tier, status, authorization_file, amount)
               VALUES (?,?,?,?,?,?,?)""",
            (eid, client_id, _json(target_urls), tier, status, authorization_file, amount),
        )
        conn.commit()
    finally:
        if own:
            conn.close()
    return eid


def add_finding(
    engagement_id: str,
    attack_class: str,
    owasp_id: str,
    cvss_score: float,
    severity: str,
    title: str,
    *,
    mitre_atlas_id: Optional[str] = None,
    evidence: Optional[str] = None,
    impact: Optional[str] = None,
    remediation: Optional[str] = None,
    finding_id: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> str:
    own = conn is None
    conn = conn or get_conn()
    fid = finding_id or new_id("fnd")
    try:
        conn.execute(
            """INSERT INTO findings
               (id, engagement_id, attack_class, owasp_id, mitre_atlas_id, cvss_score, severity, title, evidence, impact, remediation)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (fid, engagement_id, attack_class, owasp_id, mitre_atlas_id, cvss_score,
             severity, title, evidence, impact, remediation),
        )
        conn.commit()
    finally:
        if own:
            conn.close()
    return fid


def set_engagement_status(
    engagement_id: str,
    status: str,
    *,
    report_path: Optional[str] = None,
    completed: bool = False,
    conn: Optional[sqlite3.Connection] = None,
) -> None:
    own = conn is None
    conn = conn or get_conn()
    try:
        # Phase 0 (SEB_V2_MASTER_PLAN.md 0.5): an engagement may not be marked
        # delivered/completed without persisted findings and a real report file.
        if completed and status in ("delivered", "completed"):
            from integrity import IntegrityViolation

            # findings are persisted before this call — check them live.
            n = conn.execute(
                "SELECT COUNT(*) FROM findings WHERE engagement_id=?",
                (engagement_id,),
            ).fetchone()[0]
            if n == 0:
                raise IntegrityViolation(
                    f"{engagement_id}: 0 findings persisted. An engagement with no "
                    f"findings has not been performed. (A clean result is still a "
                    f"finding row — record it as 'no vulnerabilities detected'.)"
                )
            # the report file we are about to record must actually exist on disk.
            if not report_path or not os.path.exists(report_path):
                raise IntegrityViolation(
                    f"{engagement_id}: report_path missing or file absent ({report_path!r})"
                )
        if completed:
            conn.execute(
                "UPDATE engagements SET status=?, report_path=?, completed_at=? WHERE id=?",
                (status, report_path, _now_iso(), engagement_id),
            )
        else:
            conn.execute(
                "UPDATE engagements SET status=?, report_path=? WHERE id=?",
                (status, report_path, engagement_id),
            )
        conn.commit()
    finally:
        if own:
            conn.close()


def get_engagement_findings(engagement_id: str, conn=None) -> list[dict]:
    own = conn is None
    conn = conn or get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM findings WHERE engagement_id=? ORDER BY cvss_score DESC",
            (engagement_id,),
        ).fetchall()
        out = []
        for row in rows:
            if hasattr(row, "keys"):
                out.append(dict(zip(row.keys(), row)))
            else:
                cols = [d[0] for d in conn.execute("SELECT * FROM findings LIMIT 1").description]
                out.append(dict(zip(cols, row)))
        return out
    finally:
        if own:
            conn.close()


def log_intel(
    source: str,
    *,
    commit_hash: Optional[str] = None,
    new_attacks: int = 0,
    attacks_integrated: int = 0,
    novel_class: bool = False,
    run_time_ms: Optional[int] = None,
    status: str = "completed",
    conn: Optional[sqlite3.Connection] = None,
) -> str:
    own = conn is None
    conn = conn or get_conn()
    iid = new_id("int")
    try:
        conn.execute(
            """INSERT INTO intel_log
               (id, source, commit_hash, new_attacks, attacks_integrated, novel_class, run_time_ms, status)
               VALUES (?,?,?,?,?,?,?,?)""",
            (iid, source, commit_hash, new_attacks, attacks_integrated,
             int(novel_class), run_time_ms, status),
        )
        conn.commit()
    finally:
        if own:
            conn.close()
    return iid


def add_invoice(
    engagement_id: str,
    client_id: str,
    amount: float,
    *,
    stripe_invoice_id: Optional[str] = None,
    status: str = "pending",
    invoice_id: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> str:
    own = conn is None
    conn = conn or get_conn()
    iid = invoice_id or new_id("inv")
    try:
        conn.execute(
            """INSERT INTO invoices (id, engagement_id, client_id, amount, stripe_invoice_id, status)
               VALUES (?,?,?,?,?,?)""",
            (iid, engagement_id, client_id, amount, stripe_invoice_id, status),
        )
        conn.commit()
    finally:
        if own:
            conn.close()
    return iid


def _json(obj) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False)


if __name__ == "__main__":
    p = init_db()
    print(f"DB initialized at {p}")
