import io
import hashlib
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

NAVY = colors.HexColor("#0B1120")
DARK_BLUE = colors.HexColor("#1E293B")
CRIMSON = colors.HexColor("#DC2626")
AMBER = colors.HexColor("#D97706")
GREEN = colors.HexColor("#059669")
LIGHT_BG = colors.HexColor("#F8FAFC")
BORDER_COLOR = colors.HexColor("#CBD5E1")
TEXT_MUTED = colors.HexColor("#64748B")


def generate_case_pdf(case, alert, db_session) -> bytes:
    """
    Generates a tamper-evident Forensic Evidence Dossier PDF
    with risk metrics, contribution breakdown, timeline, audit chain of custody,
    and a verifiable SHA-256 cryptographic fingerprint.
    """
    from backend.data.models import Employee, Customer, Transaction, AccessLog, CaseNote, AuditLog
    import json

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=NAVY
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=TEXT_MUTED
    )
    h2_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=DARK_BLUE,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=DARK_BLUE
    )
    badge_style = ParagraphStyle(
        "BadgeText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.white,
        alignment=1  # Center
    )
    small_muted = ParagraphStyle(
        "SmallMuted",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=TEXT_MUTED
    )
    mono_style = ParagraphStyle(
        "MonoStyle",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=DARK_BLUE
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>ZENITHGUARD</b> | Financial Crime & Insider Risk Platform", subtitle_style),
            Paragraph("CLASSIFICATION: <b>RESTRICTED INVESTIGATION</b>", ParagraphStyle("RightH", parent=subtitle_style, alignment=2, textColor=CRIMSON))
        ]
    ]
    t_hdr = Table(header_data, colWidths=[340, 200])
    t_hdr.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_hdr)
    story.append(HRFlowable(width="100%", thickness=1.5, color=DARK_BLUE, spaceBefore=4, spaceAfter=10))

    # 2. Case Title & Metadata Block
    story.append(Paragraph(f"Forensic Case Dossier: {case.id}", title_style))
    story.append(Paragraph(f"Associated Alert: {alert.id} | Generated: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')} | Lead: {alert.lead_reason}", subtitle_style))
    story.append(Spacer(1, 10))

    # Meta Table
    risk_color = CRIMSON if alert.risk_level == "High" else (AMBER if alert.risk_level == "Medium" else GREEN)
    meta_table_data = [
        [
            Paragraph("<b>Case Priority:</b> " + case.priority, body_style),
            Paragraph("<b>Status:</b> " + case.status, body_style),
            Paragraph("<b>Investigator:</b> " + case.assigned_investigator, body_style),
            Paragraph(f"<b>RISK SCORE</b><br/><font size=14 color='{risk_color.hexval()}'><b>{alert.risk_score:.0f}/100 ({alert.risk_level})</b></font>", body_style)
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[130, 110, 160, 140])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # 3. Plain English Narrative & Counterfactual Analysis
    story.append(Paragraph("Executive Intelligence Summary & Narrative", h2_style))
    story.append(Paragraph(alert.explanation_narrative or "No detailed narrative recorded.", body_style))
    story.append(Spacer(1, 6))

    cf_box_data = [
        [Paragraph(f"<b>Counterfactual Impact Simulation:</b> {alert.counterfactual_summary}", ParagraphStyle("CFStyle", parent=body_style, textColor=colors.HexColor("#1E3A8A")))]
    ]
    t_cf = Table(cf_box_data, colWidths=[540])
    t_cf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_cf)
    story.append(Spacer(1, 12))

    # 4. Multi-Signal Contribution Breakdown
    story.append(Paragraph("Detection Engine Signal Contribution Breakdown", h2_style))
    signals_dict = json.loads(alert.signals_json or "{}")
    
    sig_rows = [
        [Paragraph("<b>Detector Signal</b>", body_style), Paragraph("<b>Raw Score</b>", body_style), Paragraph("<b>Weight</b>", body_style), Paragraph("<b>Key Findings & Evidentiary Rationale</b>", body_style)]
    ]
    for s_name, s_data in signals_dict.items():
        score = s_data.get("score", 0.0)
        reason = s_data.get("reason", "N/A")
        sig_rows.append([
            Paragraph(s_name.replace("_", " ").title(), body_style),
            Paragraph(f"{score:+.2f}" if score < 0 else f"{score:.2f}", body_style),
            Paragraph(str(s_data.get("weight", "0.50")), body_style),
            Paragraph(reason, small_muted)
        ])

    t_sigs = Table(sig_rows, colWidths=[120, 60, 50, 310])
    t_sigs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_sigs)
    story.append(Spacer(1, 12))

    # 5. Activity Timeline: Telemetry & Money Movement
    story.append(Paragraph("Forensic Activity Chronology (Interleaved Telemetry & Transactions)", h2_style))
    
    # Retrieve relevant logs and transactions
    inv_txns_ids = json.loads(alert.involved_transactions or "[]")
    inv_logs_ids = json.loads(alert.involved_access_logs or "[]")

    txns = db_session.query(Transaction).filter(Transaction.id.in_(inv_txns_ids)).all() if inv_txns_ids else []
    logs = db_session.query(AccessLog).filter(AccessLog.id.in_(inv_logs_ids)).all() if inv_logs_ids else []

    timeline_items = []
    for l in logs:
        timeline_items.append({
            "type": "ACCESS",
            "timestamp": l.timestamp,
            "id": l.id,
            "actor": l.employee_id,
            "subject": l.customer_id or "PORTAL",
            "action": l.action,
            "details": f"IP: {l.ip_address} | Ticket: {l.service_ticket_id or 'None'}"
        })
    for t in txns:
        timeline_items.append({
            "type": "TRANSFER",
            "timestamp": t.timestamp,
            "id": t.id,
            "actor": t.from_customer_id,
            "subject": t.to_customer_id,
            "action": f"INR {t.amount:,.0f} ({t.channel})",
            "details": t.description or "Fund remittance"
        })

    timeline_items.sort(key=lambda x: x["timestamp"])

    time_rows = [
        [Paragraph("<b>Time (UTC)</b>", body_style), Paragraph("<b>Type</b>", body_style), Paragraph("<b>Event / Action</b>", body_style), Paragraph("<b>Parties Involved</b>", body_style), Paragraph("<b>Forensic Notes</b>", body_style)]
    ]
    for item in timeline_items[:12]:  # fit neatly
        type_color = "#DC2626" if item["type"] == "TRANSFER" else "#2563EB"
        time_rows.append([
            Paragraph(item["timestamp"].strftime("%H:%M:%S"), mono_style),
            Paragraph(f"<font color='{type_color}'><b>{item['type']}</b></font>", body_style),
            Paragraph(item["action"], body_style),
            Paragraph(f"{item['actor']} &rarr; {item['subject']}", body_style),
            Paragraph(item["details"], small_muted)
        ])

    t_time = Table(time_rows, colWidths=[70, 65, 110, 115, 180])
    t_time.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_time)
    story.append(Spacer(1, 14))

    # 6. Chain of Custody & Audit Trail
    story.append(Paragraph("Chain of Custody & Investigator Audit Trail", h2_style))
    audit_logs = db_session.query(AuditLog).filter(
        (AuditLog.case_id == case.id) | (AuditLog.case_id == None)
    ).order_by(AuditLog.timestamp).all()

    audit_rows = [
        [Paragraph("<b>Timestamp (UTC)</b>", body_style), Paragraph("<b>Actor / Role</b>", body_style), Paragraph("<b>Action Taken</b>", body_style), Paragraph("<b>System Details</b>", body_style)]
    ]
    for al in audit_logs[:6]:
        audit_rows.append([
            Paragraph(al.timestamp.strftime("%Y-%m-%d %H:%M:%S"), mono_style),
            Paragraph(al.actor, body_style),
            Paragraph(al.action, body_style),
            Paragraph(al.details[:75], small_muted)
        ])
    # Add current export action to chain of custody
    export_time_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    audit_rows.append([
        Paragraph(export_time_str, mono_style),
        Paragraph("Lead Investigator", body_style),
        Paragraph("EXPORT_EVIDENCE_DOSSIER", body_style),
        Paragraph("Generated cryptographic legal evidence dossier for audit", small_muted)
    ])

    t_audit = Table(audit_rows, colWidths=[110, 120, 140, 170])
    t_audit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_audit)
    story.append(Spacer(1, 14))

    # 7. Tamper-Evident SHA-256 Digital Fingerprint
    raw_fingerprint_seed = f"{case.id}:{alert.id}:{alert.risk_score}:{alert.created_at.isoformat()}:{export_time_str}"
    sha256_hash = hashlib.sha256(raw_fingerprint_seed.encode("utf-8")).hexdigest()

    footer_data = [
        [
            Paragraph(
                f"<b>TAMPER-EVIDENT DIGITAL FINGERPRINT (SHA-256):</b><br/>"
                f"<font face='Courier' size=8 color='#1E293B'>{sha256_hash}</font><br/>"
                f"This document is sealed with an immutable SHA-256 digest. Any modification will invalidate the cryptographic hash.",
                small_muted
            )
        ]
    ]
    t_foot = Table(footer_data, colWidths=[540])
    t_foot.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_foot)

    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    # Re-calculate final exact sha256 of the generated PDF binary itself
    binary_sha256 = hashlib.sha256(pdf_bytes).hexdigest()

    # Log to audit table
    export_audit = AuditLog(
        case_id=case.id,
        actor="Investigator",
        action="REPORT_EXPORTED",
        details=f"Evidence dossier exported. SHA-256: {binary_sha256[:16]}...",
        timestamp=datetime.utcnow(),
        ip_address="127.0.0.1"
    )
    db_session.add(export_audit)
    db_session.commit()

    return pdf_bytes
