#!/usr/bin/env python3
"""SEB — Retainer Monitoring Pipeline (Weekly Cron).

Monitors retainer clients for new AI security findings by running scheduled
gauntlet scans and comparing results against previous runs. Escalates CRITICAL
new findings immediately to Klaus (SOUL.md §6).

SOUL.md §5 hard gate: Refuses to scan any client lacking a signed authorization
file in the `authorizations/` directory.
SOUL.md §7 hard gate: Scan scope is strictly limited to endpoints listed in
the signed authorization form.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from typing import Callable, Optional

# SEB Project Imports
from client_db import get_conn, init_db, add_finding, set_engagement_status
from gauntlet import run_gauntlet, EndpointTarget
from scorer import score_results, Finding
from notify import escalate

HOME = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HOME, "clients.db")
AUTH_DIR = os.path.join(HOME, "authorizations")
STATE_DIR = os.path.join(HOME, ".pipeline_state")


def _load_authorization(client_id: str) -> Optional[dict]:
    """Load a client's authorization file."""
    auth_file = os.path.join(AUTH_DIR, f"authorization_record_{client_id}.json")
    if os.path.isfile(auth_file):
        with open(auth_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _get_previous_findings(client_id: str) -> list[dict]:
    """Load previous findings for a client from their state file."""
    state_file = os.path.join(STATE_DIR, f"{client_id}_state.json")
    if os.path.isfile(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
            return state.get("findings", [])
    return []


def _save_current_findings(client_id: str, findings: list[dict]) -> None:
    """Save current findings for a client to their state file."""
    os.makedirs(STATE_DIR, exist_ok=True)
    state_file = os.path.join(STATE_DIR, f"{client_id}_state.json")
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(
            {"timestamp": datetime.now(timezone.utc).isoformat(), "findings": findings},
            f,
            indent=2,
        )


def _get_auth_target(auth_data: dict) -> EndpointTarget:
    """Create an EndpointTarget from authorization data (scope-locked)."""
    endpoint_url = auth_data.get("authorized_url")
    if not endpoint_url or not str(endpoint_url).startswith("http"):
        raise ValueError("Authorization record missing valid 'authorized_url'")
    return EndpointTarget(
        endpoint_url=endpoint_url,
        method=auth_data.get("method", "POST"),
        headers=auth_data.get("headers"),
        prompt_field=auth_data.get("prompt_field", "prompt"),
        response_field=auth_data.get("response_field", "response"),
        timeout=auth_data.get("timeout", 30),
    )


def main():
    parser = argparse.ArgumentParser(
        description="SEB Retainer Monitoring Pipeline (weekly cron)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.getcwd(),
        help="Directory for reports and logs (default: current working directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen but do not actually fire probes.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    args = parser.parse_args()

    init_db(DB_PATH)
    conn = get_conn(DB_PATH)
    conn.row_factory = sqlite3.Row

    print(f"=== SEB Retainer Monitoring Report ===")
    print(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    if args.dry_run:
        print("--- DRY RUN MODE --- No probes will be fired, no state will be saved. ---")

    clients_scanned = 0
    clients_skipped = 0
    clients_failed = 0
    new_critical_findings = 0
    new_high_findings = 0
    new_medium_findings = 0
    new_low_findings = 0
    new_info_findings = 0

    escalated_critical_items = []

    # Query for retainer clients
    clients = conn.execute(
        "SELECT id, name, company, email, tier, status FROM clients "
        "WHERE tier='retainer' OR status='active'"
    ).fetchall()

    if not clients:
        print("\nNo retainer or active clients found in the database.")
        conn.close()
        return

    # Pre-flight: refuse to run if any client lacks a signed authorization.
    for client_row in clients:
        client = dict(client_row)
        client_id = client["id"]
        client_name = f"{client['name']} ({client['company']})"
        auth_data = _load_authorization(client_id)
        if not auth_data or not auth_data.get("authorized_url"):
            print(
                f"  PRE-FLIGHT SKIP: {client_name} has no signed authorization. "
                f"Scope-lock enforced (SOUL.md §5)."
            )
            clients_skipped += 1

    for client_row in clients:
        client = dict(client_row)
        client_id = client["id"]
        client_name = f"{client['name']} ({client['company']})"

        print(f"\n--- Processing client: {client_name} (ID: {client_id}) ---")

        auth_data = _load_authorization(client_id)
        if not auth_data:
            print(f"  SKIPPED: No signed authorization file found for {client_name}.")
            clients_skipped += 1
            continue

        if not auth_data.get("authorized_url"):
            print(f"  SKIPPED: Authorization file for {client_name} missing 'authorized_url'.")
            clients_skipped += 1
            continue

        target_url = auth_data["authorized_url"]

        if args.verbose:
            print(f"  Authorization found for {client_name}. Target URL: {target_url}")

        if args.dry_run:
            print(f"  DRY RUN: Would run gauntlet against {target_url} for {client_name}.")
            clients_scanned += 1
            continue

        try:
            target_callable = _get_auth_target(auth_data)

            print(f"  Running gauntlet against {target_url}...")
            run = run_gauntlet(
                target_callable,
                target_name=target_url,
                authorization_token=str(client_id),
                limit_probes=10,
            )
            findings = score_results(run.results)
            current_findings_dicts = [f.to_dict() for f in findings]

            previous_findings_dicts = _get_previous_findings(client_id)
            previous_titles = {f["title"] for f in previous_findings_dicts}

            new_findings: list[Finding] = [
                f for f in findings if f.title not in previous_titles
            ]

            _save_current_findings(client_id, current_findings_dicts)

            print(
                f"  Gauntlet complete for {client_name}. "
                f"Probes: {run.probes_total}, Findings: {len(findings)}"
            )
            if run.errors:
                print(f"  Errors during scan: {len(run.errors)}")
                for error in run.errors:
                    print(f"    - {error}")

            if new_findings:
                print(
                    f"  New findings discovered for {client_name} "
                    f"({len(new_findings)} total new):"
                )
                for f in new_findings:
                    print(f"    - [{f.severity}] {f.title} (CVSS: {f.cvss_score})")
                    if f.severity == "CRITICAL":
                        new_critical_findings += 1
                        escalated_critical_items.append(f"{client_name}: {f.title}")
                        escalate(
                            "critical_on_retainer",
                            f"URGENT: {client_name} new CRITICAL finding: {f.title}. "
                            f"Impact: {f.impact}",
                            meta={"client_id": client_id, "finding": f.to_dict()},
                        )
                    elif f.severity == "HIGH":
                        new_high_findings += 1
                    elif f.severity == "MEDIUM":
                        new_medium_findings += 1
                    elif f.severity == "LOW":
                        new_low_findings += 1
                    elif f.severity == "INFO":
                        new_info_findings += 1

                    engagement_row = conn.execute(
                        "SELECT id FROM engagements WHERE client_id=? "
                        "ORDER BY created_at DESC LIMIT 1",
                        (client_id,),
                    ).fetchone()
                    if engagement_row:
                        add_finding(
                            engagement_id=engagement_row["id"],
                            attack_class=f.attack_class,
                            owasp_id=f.owasp_id,
                            cvss_score=f.cvss_score,
                            severity=f.severity,
                            title=f.title,
                            mitre_atlas_id=f.mitre_atlas_id,
                            evidence=f.evidence,
                            impact=f.impact,
                            remediation=f.remediation,
                            conn=conn,
                        )
                        if args.verbose:
                            print(f"    - Added new finding to DB for engagement {engagement_row['id']}")
            else:
                print(f"  No new findings for {client_name}.")

            clients_scanned += 1

        except Exception as e:
            print(f"  ERROR processing {client_name}: {e}")
            clients_failed += 1
            escalate(
                "pipeline_failure",
                f"ERROR: Retainer pipeline failed for {client_name}: {e}",
                meta={"client_id": client_id, "error": str(e)},
            )
            continue

    print(f"\n=== Cumulative Report ===")
    print(f"Clients scanned: {clients_scanned}")
    print(f"Clients skipped: {clients_skipped}")
    print(f"Clients failed: {clients_failed}")
    print("\nNew findings severity breakdown:")
    print(f"  CRITICAL: {new_critical_findings}")
    print(f"  HIGH: {new_high_findings}")
    print(f"  MEDIUM: {new_medium_findings}")
    print(f"  LOW: {new_low_findings}")
    print(f"  INFO: {new_info_findings}")

    if escalated_critical_items:
        print("\nCRITICAL items escalated:")
        for item in escalated_critical_items:
            print(f"  - {item}")
    else:
        print("\nNo CRITICAL items were escalated this run.")

    conn.close()


if __name__ == "__main__":
    main()
