"""Generate PDF match reports with ReportLab."""
import os
from datetime import datetime
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title", parent=base["Title"], fontSize=20, spaceAfter=14
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontSize=14,
            textColor=colors.HexColor("#1f4e79"), spaceBefore=12, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontSize=10, leading=14,
        ),
        "small": ParagraphStyle(
            "Small", parent=base["BodyText"], fontSize=9, leading=12,
            textColor=colors.grey,
        ),
    }


def generate_patient_report(
    patient: Dict[str, Any], match_result: Dict[str, Any]
) -> str:
    """Write a PDF report and return its filesystem path."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(
        c for c in (patient.get("patient_name") or "patient") if c.isalnum()
    ) or "patient"
    filename = f"report_{safe_name}_{timestamp}.pdf"
    path = os.path.join(REPORTS_DIR, filename)

    styles = _styles()
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    flow = []

    flow.append(Paragraph("Clinical Trial Matching Report", styles["title"]))
    flow.append(Paragraph(
        f"Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        styles["small"],
    ))
    flow.append(Spacer(1, 12))

    # Patient details
    flow.append(Paragraph("Patient Details", styles["h2"]))
    patient_rows = [
        ["Name", patient.get("patient_name", "-")],
        ["Age", str(patient.get("age", "-"))],
        ["Gender", patient.get("gender", "-") or "-"],
        ["Disease", patient.get("disease", "-") or "-"],
        ["Medication", patient.get("medication", "-") or "-"],
        ["Medical History", patient.get("medical_history", "-") or "-"],
    ]
    table = Table(patient_rows, colWidths=[4 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef3f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    flow.append(table)
    flow.append(Spacer(1, 12))

    # Best match
    best = match_result.get("best_match")
    flow.append(Paragraph("Best Match", styles["h2"]))
    if best:
        flow.append(Paragraph(f"<b>{best['title']}</b>", styles["body"]))
        flow.append(Paragraph(
            f"Disease: {best['disease']} &nbsp;|&nbsp; "
            f"Score: <b>{best['match_score']}</b> &nbsp;|&nbsp; "
            f"Eligible: <b>{best['eligible']}</b>",
            styles["body"],
        ))
        flow.append(Paragraph(f"Reason: {best['reason']}", styles["body"]))
        flow.append(Paragraph(
            f"Recommendation: {best['recommendation']}", styles["body"]
        ))
    else:
        flow.append(Paragraph("No matching trials found.", styles["body"]))
    flow.append(Spacer(1, 12))

    # Retrieved trials table
    flow.append(Paragraph("Retrieved Trials", styles["h2"]))
    retrieved = match_result.get("retrieved_trials", [])
    if retrieved:
        header = ["#", "Title", "Disease", "Score", "Eligible", "Recommendation"]
        data = [header]
        for i, t in enumerate(retrieved, start=1):
            data.append([
                str(i),
                Paragraph(str(t.get("title", "")), styles["body"]),
                str(t.get("disease", "")),
                str(t.get("match_score", "")),
                "Yes" if t.get("eligible") else "No",
                Paragraph(str(t.get("recommendation", "")), styles["body"]),
            ])
        trial_table = Table(
            data,
            colWidths=[0.8 * cm, 5 * cm, 3 * cm, 1.5 * cm, 1.7 * cm, 4 * cm],
            repeatRows=1,
        )
        trial_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        flow.append(trial_table)
    else:
        flow.append(Paragraph("No trials were retrieved.", styles["body"]))

    flow.append(Spacer(1, 18))
    flow.append(Paragraph(
        "This report is generated by an AI system and is intended for clinical "
        "decision support only. Final eligibility determination must be made "
        "by a qualified clinician.",
        styles["small"],
    ))

    doc.build(flow)
    return path
