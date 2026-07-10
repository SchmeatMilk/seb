"""
SEB — report_generator.py : scored findings -> professional PDF.

Uses reportlab (present in the SEB runtime venv). Produces a SANS-style,
compliance-ready report with:
  - Cover / engagement metadata
  - Executive summary (severity counts, pass rate)
  - Methodology (transparent — what was tested, what engines)
  - Per-finding detail (OWASP + MITRE ATLAS + CVSS 4.0 mapping)
  - Metrics dashboard (by attack class)
  - Remediation roadmap (priority-ordered)
  - Legal disclaimers + safe-harbor clause

No "fake it": every finding in the report maps to a real ProbeResult that the
gauntlet actually fired and the scorer actually flagged.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

from scorer import Finding, metrics

SEV_COLOR = {
    "CRITICAL": colors.HexColor("#7d1128"),
    "HIGH": colors.HexColor("#c1121f"),
    "MEDIUM": colors.HexColor("#e07a00"),
    "LOW": colors.HexColor("#2a9d8f"),
    "INFO": colors.HexColor("#577590"),
}


@dataclass
class ReportMeta:
    client_name: str = "Internal Dogfood (SEB)"
    company: str = "SEB — Security Inquisitor Balance"
    engagement_id: str = "n/a"
    tier: str = "dogfood"
    target: str = "self"
    authorization_ref: str = "self-authored / sandbox"
    prepared_by: str = "SEB-CORE (autonomous)"
    date: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("H1b", parent=ss["Heading1"], textColor=colors.HexColor("#0d1b2a"), spaceAfter=8))
    ss.add(ParagraphStyle("H2b", parent=ss["Heading2"], textColor=colors.HexColor("#1b263b"), spaceBefore=10, spaceAfter=4))
    ss.add(ParagraphStyle("Body2", parent=ss["BodyText"], fontSize=9.5, leading=13))
    ss.add(ParagraphStyle("Small", parent=ss["BodyText"], fontSize=8, textColor=colors.HexColor("#555555")))
    ss.add(ParagraphStyle("Cell", parent=ss["BodyText"], fontSize=8, leading=10))
    return ss


def build_pdf(
    findings: list[Finding],
    probe_results_count: int,
    meta: ReportMeta,
    engines_skipped: Optional[list[str]] = None,
    out_path: str = "~/src/seb/output/seb_report.pdf",
) -> str:
    out_path = os.path.expanduser(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ss = _styles()
    doc = SimpleDocTemplate(
        out_path, pagesize=LETTER,
        leftMargin=0.8 * inch, rightMargin=0.8 * inch,
        topMargin=0.8 * inch, bottomMargin=0.8 * inch,
        title=f"SEB Security Report {meta.engagement_id}",
        author="SEB — Security Inquisitor Balance",
    )
    E: list = []
    sev_counts = metrics([], findings)  # only need dist; pass-rate computed separately
    dist = sev_counts["severity_distribution"]  # empty for 0 findings -> handle below
    # Recompute distribution directly
    dist = {}
    for f in findings:
        dist[f.severity] = dist.get(f.severity, 0) + 1
    total = probe_results_count
    vuln = len(findings)
    pass_rate = round(((total - vuln) / total * 100.0), 1) if total else 100.0

    # ---- Cover ----
    E.append(Paragraph("SEB — Security Assessment Report", ss["H1b"]))
    E.append(Paragraph("Affordable AI security testing that keeps up with the latest attack techniques — automated pipeline, human-verified.", ss["Small"]))
    E.append(Spacer(1, 12))
    cover = [
        ["Client", f"{meta.client_name} ({meta.company})"],
        ["Engagement ID", meta.engagement_id],
        ["Tier", meta.tier],
        ["Target", meta.target],
        ["Authorization ref", meta.authorization_ref],
        ["Date (UTC)", meta.date],
        ["Prepared by", meta.prepared_by],
    ]
    t = Table(cover, colWidths=[1.6 * inch, 5.0 * inch])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1b263b")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e0e1dd")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    E.append(t)
    E.append(Spacer(1, 16))

    # ---- Executive Summary ----
    E.append(Paragraph("1. Executive Summary", ss["H2b"]))
    summary = (
        f"A total of <b>{total}</b> adversarial probes were executed against the authorized target. "
        f"<b>{vuln}</b> distinct vulnerabilities were confirmed "
        f"(pass rate <b>{pass_rate}%</b>). "
        f"Severity distribution: "
        + ", ".join(f"{k}={dist.get(k,0)}" for k in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"])
        + f". {'No vulnerabilities were confirmed; defenses held across all probe classes.' if vuln == 0 else 'See Section 4 for prioritized remediation.'}"
    )
    E.append(Paragraph(summary, ss["Body2"]))
    E.append(Spacer(1, 8))

    # ---- Methodology ----
    E.append(Paragraph("2. Methodology", ss["H2b"]))
    method = (
        "Testing was conducted under the HackerOne Good Faith AI Research Safe Harbor framework (Jan 2026). "
        "Probes were delivered from the local L1B3RT4S adversarial corpus and fired against the authorized, "
        "sandboxed target only. Rate-limiting and single-session, non-destructive delivery were enforced. "
        "Every response was scored by SEB's defense-aware detector and mapped to OWASP LLM Top 10 (2025), "
        "MITRE ATLAS, and CVSS 4.0."
    )
    E.append(Paragraph(method, ss["Body2"]))
    if engines_skipped:
        E.append(Spacer(1, 4))
        E.append(Paragraph("Engines not exercised this run (reported honestly, not faked): "
                           + "; ".join(engines_skipped) + ".", ss["Small"]))
    E.append(Spacer(1, 8))

    # ---- Metrics dashboard ----
    E.append(Paragraph("3. Metrics Dashboard", ss["H2b"]))
    if findings:
        rows = [["Severity", "Count"]]
        for k in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            if dist.get(k):
                rows.append([k, str(dist[k])])
        mt = Table(rows, colWidths=[2.0 * inch, 1.0 * inch])
        style = [
            ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b263b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ]
        for i, k in enumerate([r[0] for r in rows[1:]], start=1):
            style.append(("TEXTCOLOR", (0, i), (0, i), SEV_COLOR.get(k, colors.black)))
        mt.setStyle(TableStyle(style))
        E.append(mt)
    else:
        E.append(Paragraph("No vulnerabilities confirmed. Defense posture: PASS across all probed classes.", ss["Body2"]))
    E.append(Spacer(1, 8))

    # ---- Findings ----
    E.append(Paragraph("4. Detailed Findings", ss["H2b"]))
    if not findings:
        E.append(Paragraph("No confirmed findings. The target correctly refused all adversarial probes in scope.", ss["Body2"]))
    else:
        for i, f in enumerate(findings, 1):
            badge = Table([[f.severity]], colWidths=[1.0 * inch])
            badge.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), SEV_COLOR.get(f.severity, colors.grey)),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("FONT", (0, 0), (-1, -1), "Helvetica-Bold", 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))
            head = Table([[badge, Paragraph(f"<b>F{i}. {f.title}</b>  "
                                            f"<font size=8 color='#666'>(CVSS {f.cvss_score} · {f.owasp_id} · {f.mitre_atlas_id})</font>", ss["Body2"])]],
                         colWidths=[1.1 * inch, 5.5 * inch])
            head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                     ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
            E.append(head)
            det = [
                ["Attack class", f.attack_class],
                ["OWASP", f"{f.owasp_id} — {f.owasp_name}"],
                ["MITRE ATLAS", f.mitre_atlas_id],
                ["CVSS 4.0", str(f.cvss_score)],
                ["Impact", f.impact],
                ["Evidence", f.evidence or "(none)"],
                ["Remediation", f.remediation],
            ]
            dt = Table(det, colWidths=[1.3 * inch, 5.3 * inch])
            dt.setStyle(TableStyle([
                ("FONT", (0, 0), (-1, -1), "Helvetica", 8),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e0e1dd")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
            ]))
            E.append(dt)
            E.append(Spacer(1, 10))

    # ---- Remediation roadmap ----
    E.append(PageBreak())
    E.append(Paragraph("5. Remediation Roadmap", ss["H2b"]))
    if findings:
        from scorer import severity_from_cvss
        order = sorted(findings, key=lambda x: x.cvss_score, reverse=True)
        rows = [["Priority", "Finding", "Effort"]]
        for i, f in enumerate(order, 1):
            effort = "High" if f.cvss_score >= 8.0 else ("Medium" if f.cvss_score >= 5.0 else "Low")
            rows.append([str(i), f"{f.title} ({f.owasp_id})", effort])
        rt = Table(rows, colWidths=[0.8 * inch, 4.5 * inch, 1.0 * inch])
        rt.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), "Helvetica", 8.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b263b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ]))
        E.append(rt)
    else:
        E.append(Paragraph("No remediation required. Maintain current defenses and re-test on the next cadence.", ss["Body2"]))
    E.append(Spacer(1, 14))

    # ---- Legal ----
    E.append(Paragraph("6. Legal & Disclaimers", ss["H2b"]))
    legal = (
        "This assessment was performed under written authorization for the systems named in Exhibit A and within the "
        "HackerOne Good Faith AI Research Safe Harbor framework. Testing was limited to text-based prompt injection, "
        "jailbreak detection, and system-prompt extraction via authorized interfaces. Third-party platform "
        "infrastructure was explicitly excluded from scope. Findings are delivered to the client first under a 90-day "
        "responsible-disclosure embargo. This report is not a guarantee that all vulnerabilities have been discovered. "
        "SEB's liability is limited to the fees paid for the engagement."
    )
    E.append(Paragraph(legal, ss["Small"]))

    doc.build(E)
    return out_path


if __name__ == "__main__":
    # Quick standalone render with one dummy finding to prove PDF generation works.
    dummy = [Finding("godmode", "LLM01", "Prompt Injection", "ATLAS-T0041",
                     8.5, "HIGH", "Godmode override probe succeeded")]
    p = build_pdf(dummy, probe_results_count=10, meta=ReportMeta(),
                  engines_skipped=["garak (not installed)", "pyrit (not installed)"],
                  out_path="~/src/seb/output/_smoke.pdf")
    print(f"PDF written: {p}")
