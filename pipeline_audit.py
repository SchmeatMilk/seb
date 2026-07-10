"""
SEB — pipeline_audit.py : full audit orchestrator (Phase 1→2).

Flow (from SEB_PLAN_V2.md §7.1, minus the human-gated commercial steps):
  intake -> authorize check -> gauntlet -> scorer -> report -> DB log

This module is the autonomous core. It will NOT:
  - send email / upload to GitHub (parked for Malik: §8 delivery, Stripe)
  - auto-post to LinkedIn
  - run against any target lacking an authorization token

It WILL produce a valid PDF and persist the engagement + findings to clients.db,
and (for dogfood) verifies SEB's own defenses hold.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Optional

from client_db import add_client, add_engagement, add_finding, set_engagement_status, init_db, new_id
from gauntlet import run_gauntlet, DefendedSimTarget, VulnerableSimTarget
from scorer import score_results, metrics
from report_generator import build_pdf, ReportMeta

SOUL_PATH = os.path.expanduser("~/AppData/Local/hermes/profiles/seb/SOUL.md")
DB_PATH = os.path.expanduser("~/src/seb/clients.db")
OUT_DIR = os.path.expanduser("~/src/seb/output")


@dataclass
class AuditConfig:
    client_name: str
    company: str
    email: str
    target_name: str
    authorization_token: str
    target: Callable[[str], str]
    tier: str = "dogfood"
    engines: Optional[list[str]] = None
    limit_probes: Optional[int] = None
    report_name: str = "seb_report.pdf"
    persist: bool = True
    rate_interval_s: float = 1.0


def run_audit(cfg: AuditConfig) -> dict:
    init_db(DB_PATH)
    run = run_gauntlet(
        cfg.target,
        target_name=cfg.target_name,
        authorization_token=cfg.authorization_token,
        engines=cfg.engines,
        limit_probes=cfg.limit_probes,
        rate_interval_s=cfg.rate_interval_s,
    )
    findings = score_results(run.results)
    m = metrics(run.results, findings)

    meta = ReportMeta(
        client_name=cfg.client_name, company=cfg.company,
        tier=cfg.tier, target=cfg.target_name,
        authorization_ref=cfg.authorization_token,
    )
    out_path = os.path.join(OUT_DIR, cfg.report_name)
    pdf = build_pdf(findings, probe_results_count=run.probes_total,
                    meta=meta, engines_skipped=run.skipped_engines, out_path=out_path)

    result = {
        "probes_fired": run.probes_total,
        "findings": len(findings),
        "metrics": m,
        "skipped_engines": run.skipped_engines,
        "stopped_early": run.stopped_early,
        "pdf": pdf,
    }

    if cfg.persist:
        cid = add_client(cfg.client_name, cfg.company, cfg.email,
                         tier=cfg.tier, status="active", source="dogfood")
        eid = add_engagement(cid, [cfg.target_name], cfg.tier,
                              authorization_file=cfg.authorization_token)
        for f in findings:
            add_finding(eid, f.attack_class, f.owasp_id, f.cvss_score, f.severity,
                        f.title, mitre_atlas_id=f.mitre_atlas_id, evidence=f.evidence,
                        impact=f.impact, remediation=f.remediation)
        set_engagement_status(eid, "delivered", report_path=pdf, completed=True)
        result["client_id"] = cid
        result["engagement_id"] = eid

    result["findings_detail"] = [f.to_dict() for f in findings]
    return result


def dogfood_self() -> dict:
    """Run the gauntlet against SEB's own SOUL.md (defended). Expect 0 findings."""
    soul = os.path.expanduser(SOUL_PATH)
    if not os.path.isfile(soul):
        soul = os.path.expanduser("~/src/seb/00_HANDOFF.md")
    tgt = DefendedSimTarget(soul)
    cfg = AuditConfig(
        client_name="SEB (self)", company="Security Inquisitor Balance",
        email="ops@seb.security", target_name="SEB-SOUL-dogfood",
        authorization_token="SELF-AUTH-sandbox-dogfood",
        target=tgt, tier="dogfood", engines=["l1b3rt4s"],
        report_name="seb_dogfood_self.pdf",
    )
    # Local sandbox sim: rate-limit is for real external targets; near-zero here.
    cfg.rate_interval_s = 0.01
    return run_audit(cfg)


if __name__ == "__main__":
    import json
    r = dogfood_self()
    print(json.dumps({k: v for k, v in r.items() if k != "findings_detail"}, indent=2, default=str))
    if r["findings"] == 0:
        print("\nDOGFOOD PASS: SEB's own defenses held against the full L1B3RT4S corpus (0 leaks).")
    else:
        print(f"\nDOGFOOD FLAG: {r['findings']} confirmed leaks against own SOUL — review defenses.")
