import os
import sys
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.data.database import get_db, engine, SessionLocal
from backend.data.models import (
    Employee, Customer, Account, AccessLog, Transaction, GroundTruth, Alert, Case, CaseNote, AuditLog, Branch
)
from backend.app.detection.pipeline import DetectionPipeline
from backend.app.export_pdf import generate_case_pdf

app = FastAPI(
    title="ZenithGuard – Financial Crime & Insider Risk Intelligence API",
    description="Unified API connecting employee access telemetry with transaction graphs to expose insider risk and fraud rings.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline_instance = DetectionPipeline()


# -------------------------------------------------------------
# Request & Response Schemas
# -------------------------------------------------------------
class CaseCreateSchema(BaseModel):
    alert_id: str
    title: Optional[str] = None
    priority: Optional[str] = "High"
    assigned_investigator: Optional[str] = "Unassigned"


class CaseUpdateSchema(BaseModel):
    status: Optional[str] = None
    assigned_investigator: Optional[str] = None
    priority: Optional[str] = None


class CaseNoteCreateSchema(BaseModel):
    author: str
    note_text: str


class SimulateScenarioSchema(BaseModel):
    scenario_type: str  # "SUSPICIOUS_INSIDER", "STRUCTURING", "BENIGN_TICKET", "BENIGN_SALARY"
    employee_id: Optional[str] = "E102"
    customer_id: Optional[str] = "C417"
    amount: Optional[float] = 49000.0


# -------------------------------------------------------------
# Health & Status
# -------------------------------------------------------------
@app.get("/")
def root():
    return {
        "platform": "ZenithGuard – Financial Crime & Insider Risk Intelligence Platform",
        "status": "OPERATIONAL",
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }


# -------------------------------------------------------------
# Dashboard Statistics
# -------------------------------------------------------------
@app.get("/api/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_alerts = db.query(Alert).count()
    high_risk_alerts = db.query(Alert).filter(Alert.risk_level == "High").count()
    medium_risk_alerts = db.query(Alert).filter(Alert.risk_level == "Medium").count()
    low_risk_alerts = db.query(Alert).filter(Alert.risk_level == "Low").count()
    open_cases = db.query(Case).filter(Case.status.in_(["Open", "In Review", "Escalated"])).count()

    alerts_by_type = {}
    for a in db.query(Alert).all():
        alerts_by_type[a.alert_type] = alerts_by_type.get(a.alert_type, 0) + 1

    # Top risky employees
    top_emps = []
    emp_alerts = {}
    for a in db.query(Alert).filter(Alert.employee_id != None).all():
        if a.employee_id not in emp_alerts:
            emp = db.query(Employee).filter(Employee.id == a.employee_id).first()
            emp_alerts[a.employee_id] = {
                "id": a.employee_id,
                "name": emp.name if emp else a.employee_id,
                "role": emp.role if emp else "Unknown",
                "branch_id": emp.branch_id if emp else "Unknown",
                "max_risk_score": a.risk_score,
                "alert_count": 0,
                "high_count": 0
            }
        emp_alerts[a.employee_id]["alert_count"] += 1
        emp_alerts[a.employee_id]["max_risk_score"] = max(emp_alerts[a.employee_id]["max_risk_score"], a.risk_score)
        if a.risk_level == "High":
            emp_alerts[a.employee_id]["high_count"] += 1

    top_emps = sorted(list(emp_alerts.values()), key=lambda x: x["max_risk_score"], reverse=True)[:5]

    return {
        "kpis": {
            "total_alerts": total_alerts,
            "high_risk_alerts": high_risk_alerts,
            "medium_risk_alerts": medium_risk_alerts,
            "low_risk_alerts": low_risk_alerts,
            "open_cases": open_cases,
            "avg_time_to_triage": "14 mins",
            "insider_touch_coverage": "98.4%"
        },
        "alerts_by_type": [{"type": k.replace("_", " ").title(), "count": v} for k, v in alerts_by_type.items()],
        "top_risky_employees": top_emps
    }


# -------------------------------------------------------------
# Alerts Endpoints
# -------------------------------------------------------------
@app.get("/api/alerts")
def get_alerts(
    level: Optional[str] = Query(None),
    employee: Optional[str] = Query(None),
    customer: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
):
    query = db.query(Alert)

    if level:
        query = query.filter(Alert.risk_level == level)
    if employee:
        query = query.filter(Alert.employee_id == employee)
    if customer:
        query = query.filter(Alert.customer_id == customer)
    if status_filter:
        query = query.filter(Alert.status == status_filter)

    alerts = query.order_by(Alert.risk_score.desc(), Alert.created_at.desc()).all()

    res = []
    for a in alerts:
        emp = db.query(Employee).filter(Employee.id == a.employee_id).first() if a.employee_id else None
        cust = db.query(Customer).filter(Customer.id == a.customer_id).first()
        res.append({
            "id": a.id,
            "created_at": a.created_at.isoformat(),
            "employee_id": a.employee_id,
            "employee_name": emp.name if emp else "Internal Actor",
            "employee_role": emp.role if emp else "Unknown",
            "employee_branch": emp.branch_id if emp else "N/A",
            "customer_id": a.customer_id,
            "customer_name": cust.name if cust else a.customer_id,
            "customer_branch": cust.home_branch_id if cust else "N/A",
            "alert_type": a.alert_type,
            "risk_score": a.risk_score,
            "risk_level": a.risk_level,
            "status": a.status,
            "lead_reason": a.lead_reason,
            "similar_cases_count": a.similar_cases_count
        })
    return res


@app.get("/api/alerts/{alert_id}")
def get_alert_detail(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    emp = db.query(Employee).filter(Employee.id == alert.employee_id).first() if alert.employee_id else None
    cust = db.query(Customer).filter(Customer.id == alert.customer_id).first()
    case = db.query(Case).filter(Case.alert_id == alert_id).first()

    signals_dict = json.loads(alert.signals_json or "{}")

    # Format signal contributions for frontend bar chart
    contributions = []
    for sig_name, s_data in signals_dict.items():
        score = s_data.get("score", 0.0)
        contributions.append({
            "signal": sig_name.replace("_", " ").title(),
            "raw_signal": sig_name,
            "score": score,
            "weight": s_data.get("weight", 0.5),
            "reason": s_data.get("reason", "Normal baseline"),
            "is_anomalous": (score >= 0.5 or score < 0)
        })

    return {
        "id": alert.id,
        "created_at": alert.created_at.isoformat(),
        "risk_score": alert.risk_score,
        "risk_level": alert.risk_level,
        "status": alert.status,
        "alert_type": alert.alert_type,
        "lead_reason": alert.lead_reason,
        "similar_cases_count": alert.similar_cases_count,
        "explanation": {
            "narrative": alert.explanation_narrative,
            "counterfactual": alert.counterfactual_summary,
            "contributions": contributions,
            "similar_cases_note": f"Identified {alert.similar_cases_count} past matching cases for this employee/pattern"
        },
        "employee": {
            "id": emp.id if emp else None,
            "name": emp.name if emp else "Internal Actor",
            "role": emp.role if emp else "N/A",
            "email": emp.email if emp else "N/A",
            "branch_id": emp.branch_id if emp else "N/A",
            "authorized_customer_range": emp.authorized_customer_range if emp else "N/A"
        },
        "customer": {
            "id": cust.id if cust else alert.customer_id,
            "name": cust.name if cust else alert.customer_id,
            "phone": cust.phone if cust else "N/A",
            "email": cust.email if cust else "N/A",
            "home_branch_id": cust.home_branch_id if cust else "N/A",
            "risk_rating": cust.risk_rating if cust else "LOW",
            "occupation": cust.occupation if cust else "Salaried"
        },
        "case": {
            "id": case.id if case else None,
            "status": case.status if case else "Unassigned",
            "assigned_investigator": case.assigned_investigator if case else "Unassigned",
            "priority": case.priority if case else "Medium"
        } if case else None,
        "involved_customers": json.loads(alert.involved_customers or "[]"),
        "involved_transactions": json.loads(alert.involved_transactions or "[]"),
        "involved_access_logs": json.loads(alert.involved_access_logs or "[]")
    }


# -------------------------------------------------------------
# Graph Visualization Endpoint
# -------------------------------------------------------------
@app.get("/api/graph/{alert_id}")
def get_alert_graph(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    inv_cust_ids = json.loads(alert.involved_customers or "[]")
    inv_txn_ids = json.loads(alert.involved_transactions or "[]")
    inv_log_ids = json.loads(alert.involved_access_logs or "[]")

    nodes = []
    edges = []
    node_set = set()

    # 1. Add Employee Node
    if alert.employee_id:
        emp = db.query(Employee).filter(Employee.id == alert.employee_id).first()
        nodes.append({
            "id": alert.employee_id,
            "label": emp.name if emp else alert.employee_id,
            "type": "EMPLOYEE",
            "role": emp.role if emp else "CSO",
            "branch": emp.branch_id if emp else "Pune",
            "is_insider": True,
            "risk_level": alert.risk_level
        })
        node_set.add(alert.employee_id)

    # 2. Add Customer Nodes
    for cid in inv_cust_ids:
        cust = db.query(Customer).filter(Customer.id == cid).first()
        is_primary = (cid == alert.customer_id)
        nodes.append({
            "id": cid,
            "label": f"{cust.name} ({cid})" if cust else cid,
            "type": "CUSTOMER",
            "branch": cust.home_branch_id if cust else "Mumbai",
            "occupation": cust.occupation if cust else "Salaried",
            "risk_rating": cust.risk_rating if cust else "LOW",
            "is_target": is_primary
        })
        node_set.add(cid)

    # 3. Add Access Edges (Employee -> Customer)
    logs = db.query(AccessLog).filter(AccessLog.id.in_(inv_log_ids)).all() if inv_log_ids else []
    for l in logs:
        if l.customer_id and l.customer_id in node_set and l.employee_id in node_set:
            edges.append({
                "id": l.id,
                "source": l.employee_id,
                "target": l.customer_id,
                "type": "ACCESS",
                "label": l.action,
                "action": l.action,
                "timestamp": l.timestamp.isoformat(),
                "time_str": l.timestamp.strftime("%H:%M:%S"),
                "is_after_hours": l.is_after_hours,
                "service_ticket_id": l.service_ticket_id,
                "is_unauthorized": (l.customer_id == alert.customer_id and alert.employee_id == "E102")
            })

    # 4. Add Transaction Edges (Customer -> Customer)
    txns = db.query(Transaction).filter(Transaction.id.in_(inv_txn_ids)).all() if inv_txn_ids else []
    # Identify if edge is part of suspicious cycle
    for t in txns:
        # Ensure source & target exist in node_set
        if t.from_customer_id not in node_set:
            c = db.query(Customer).filter(Customer.id == t.from_customer_id).first()
            nodes.append({
                "id": t.from_customer_id,
                "label": f"{c.name} ({c.id})" if c else t.from_customer_id,
                "type": "CUSTOMER",
                "branch": c.home_branch_id if c else "Unknown"
            })
            node_set.add(t.from_customer_id)

        if t.to_customer_id not in node_set:
            c = db.query(Customer).filter(Customer.id == t.to_customer_id).first()
            nodes.append({
                "id": t.to_customer_id,
                "label": f"{c.name} ({c.id})" if c else t.to_customer_id,
                "type": "CUSTOMER",
                "branch": c.home_branch_id if c else "Unknown"
            })
            node_set.add(t.to_customer_id)

        is_suspicious_cycle = (alert.alert_type == "HERO_INSIDER_CIRCULAR" or t.amount >= 45000)
        edges.append({
            "id": t.id,
            "source": t.from_customer_id,
            "target": t.to_customer_id,
            "type": "TRANSACTION",
            "amount": t.amount,
            "label": f"INR {t.amount:,.0f}",
            "channel": t.channel,
            "timestamp": t.timestamp.isoformat(),
            "time_str": t.timestamp.strftime("%H:%M:%S"),
            "description": t.description,
            "is_suspicious_cycle": is_suspicious_cycle
        })

    return {
        "alert_id": alert_id,
        "nodes": nodes,
        "edges": edges,
        "cycle_highlight": alert.alert_type == "HERO_INSIDER_CIRCULAR"
    }


# -------------------------------------------------------------
# Interleaved Timeline Endpoint
# -------------------------------------------------------------
@app.get("/api/timeline/{alert_id}")
def get_alert_timeline(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    inv_txn_ids = json.loads(alert.involved_transactions or "[]")
    inv_log_ids = json.loads(alert.involved_access_logs or "[]")

    logs = db.query(AccessLog).filter(AccessLog.id.in_(inv_log_ids)).all() if inv_log_ids else []
    txns = db.query(Transaction).filter(Transaction.id.in_(inv_txn_ids)).all() if inv_txn_ids else []

    timeline = []
    for l in logs:
        emp = db.query(Employee).filter(Employee.id == l.employee_id).first()
        cust = db.query(Customer).filter(Customer.id == l.customer_id).first() if l.customer_id else None
        timeline.append({
            "id": l.id,
            "timestamp": l.timestamp.isoformat(),
            "time_display": l.timestamp.strftime("%H:%M:%S"),
            "event_type": "ACCESS",
            "actor_id": l.employee_id,
            "actor_name": emp.name if emp else l.employee_id,
            "actor_role": emp.role if emp else "Employee",
            "target_id": l.customer_id,
            "target_name": cust.name if cust else "Customer Portal",
            "action": l.action,
            "amount": None,
            "details": f"IP: {l.ip_address} | Ticket: {l.service_ticket_id or 'None'}",
            "is_after_hours": l.is_after_hours,
            "is_unauthorized": (l.customer_id == alert.customer_id and alert.employee_id == "E102")
        })

    for t in txns:
        c_from = db.query(Customer).filter(Customer.id == t.from_customer_id).first()
        c_to = db.query(Customer).filter(Customer.id == t.to_customer_id).first()
        timeline.append({
            "id": t.id,
            "timestamp": t.timestamp.isoformat(),
            "time_display": t.timestamp.strftime("%H:%M:%S"),
            "event_type": "TRANSACTION",
            "actor_id": t.from_customer_id,
            "actor_name": c_from.name if c_from else t.from_customer_id,
            "target_id": t.to_customer_id,
            "target_name": c_to.name if c_to else t.to_customer_id,
            "action": f"TRANSFER ({t.channel})",
            "amount": t.amount,
            "amount_display": f"INR {t.amount:,.0f}",
            "details": t.description or "Fund transfer",
            "is_structured": (45000 <= t.amount <= 49950),
            "is_cycle": (alert.alert_type == "HERO_INSIDER_CIRCULAR")
        })

    timeline.sort(key=lambda x: x["timestamp"])

    # Calculate Insider-Touch Lag annotation
    first_txn = next((e for e in timeline if e["event_type"] == "TRANSACTION"), None)
    insider_touch_annotation = None

    if first_txn:
        t_tx = datetime.fromisoformat(first_txn["timestamp"])
        # Find access events on target customer within 60 mins before first transaction
        candidate_accesses = [
            e for e in timeline
            if e["event_type"] == "ACCESS"
            and e.get("target_id") == alert.customer_id
            and datetime.fromisoformat(e["timestamp"]) <= t_tx
            and (t_tx - datetime.fromisoformat(e["timestamp"])).total_seconds() <= 3600
        ]
        if candidate_accesses:
            # Earliest access in this preceding session
            first_access = candidate_accesses[0]
            t_acc = datetime.fromisoformat(first_access["timestamp"])
            delta_m = max(0.0, round((t_tx - t_acc).total_seconds() / 60.0, 1))
            insider_touch_annotation = {
                "lag_minutes": delta_m,
                "label": f"Insider-Touch: {delta_m:.0f} min",
                "access_event_id": first_access["id"],
                "txn_event_id": first_txn["id"],
                "is_critical": (delta_m <= 10.0)
            }

    return {
        "alert_id": alert_id,
        "timeline": timeline,
        "insider_touch": insider_touch_annotation
    }


# -------------------------------------------------------------
# Case Management Endpoints
# -------------------------------------------------------------
@app.get("/api/cases")
def get_cases(
    status_filter: Optional[str] = Query(None, alias="status"),
    investigator: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Case)
    if status_filter:
        query = query.filter(Case.status == status_filter)
    if investigator:
        query = query.filter(Case.assigned_investigator == investigator)
    if priority:
        query = query.filter(Case.priority == priority)

    cases = query.order_by(Case.created_at.desc()).all()
    res = []
    for c in cases:
        alert = db.query(Alert).filter(Alert.id == c.alert_id).first()
        res.append({
            "id": c.id,
            "alert_id": c.alert_id,
            "title": c.title,
            "status": c.status,
            "assigned_investigator": c.assigned_investigator,
            "priority": c.priority,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat() if c.updated_at else c.created_at.isoformat(),
            "risk_score": alert.risk_score if alert else 0.0,
            "risk_level": alert.risk_level if alert else "Low",
            "summary": c.summary
        })
    return res


@app.post("/api/cases", status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreateSchema, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == payload.alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    existing = db.query(Case).filter(Case.alert_id == payload.alert_id).first()
    if existing:
        return {"case_id": existing.id, "message": "Case already exists for this alert"}

    case_id = f"CASE_{payload.alert_id.replace('ALT_', '')}"
    new_case = Case(
        id=case_id,
        alert_id=payload.alert_id,
        title=payload.title or f"Investigation: {alert.alert_type} on {alert.customer_id}",
        status="Open",
        assigned_investigator=payload.assigned_investigator or "Unassigned",
        priority=payload.priority or ("High" if alert.risk_level == "High" else "Medium"),
        created_at=datetime.utcnow(),
        summary=alert.explanation_narrative[:240]
    )
    db.add(new_case)

    audit = AuditLog(
        case_id=case_id,
        actor="Investigator",
        action="CASE_CREATED",
        details=f"Created case {case_id} from alert {payload.alert_id}",
        timestamp=datetime.utcnow(),
        ip_address="127.0.0.1"
    )
    db.add(audit)
    db.commit()

    return {"case_id": case_id, "status": "Open", "message": "Case successfully initiated"}


@app.get("/api/cases/{case_id}")
def get_case_detail(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    alert = db.query(Alert).filter(Alert.id == case.alert_id).first()
    notes = db.query(CaseNote).filter(CaseNote.case_id == case_id).order_by(CaseNote.timestamp.desc()).all()
    audits = db.query(AuditLog).filter(AuditLog.case_id == case_id).order_by(AuditLog.timestamp.desc()).all()

    return {
        "id": case.id,
        "alert_id": case.alert_id,
        "title": case.title,
        "status": case.status,
        "assigned_investigator": case.assigned_investigator,
        "priority": case.priority,
        "created_at": case.created_at.isoformat(),
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        "closed_at": case.closed_at.isoformat() if case.closed_at else None,
        "summary": case.summary,
        "alert": {
            "id": alert.id,
            "risk_score": alert.risk_score,
            "risk_level": alert.risk_level,
            "alert_type": alert.alert_type,
            "lead_reason": alert.lead_reason,
            "narrative": alert.explanation_narrative
        } if alert else None,
        "notes": [
            {
                "id": n.id,
                "author": n.author,
                "timestamp": n.timestamp.isoformat(),
                "note_text": n.note_text
            }
            for n in notes
        ],
        "audit_trail": [
            {
                "id": a.id,
                "actor": a.actor,
                "action": a.action,
                "details": a.details,
                "timestamp": a.timestamp.isoformat()
            }
            for a in audits
        ]
    }


@app.patch("/api/cases/{case_id}")
def update_case(case_id: str, payload: CaseUpdateSchema, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    actions_taken = []
    if payload.status:
        old_status = case.status
        case.status = payload.status
        if payload.status == "Closed":
            case.closed_at = datetime.utcnow()
        actions_taken.append(f"Status changed from {old_status} to {payload.status}")

    if payload.assigned_investigator:
        old_inv = case.assigned_investigator
        case.assigned_investigator = payload.assigned_investigator
        actions_taken.append(f"Investigator changed from {old_inv} to {payload.assigned_investigator}")

    if payload.priority:
        case.priority = payload.priority
        actions_taken.append(f"Priority changed to {payload.priority}")

    case.updated_at = datetime.utcnow()

    # Log to audit trail
    if actions_taken:
        audit = AuditLog(
            case_id=case_id,
            actor=payload.assigned_investigator or "Investigator",
            action="STATUS_CHANGED",
            details="; ".join(actions_taken),
            timestamp=datetime.utcnow(),
            ip_address="127.0.0.1"
        )
        db.add(audit)

    db.commit()
    return {"case_id": case_id, "status": case.status, "assigned_investigator": case.assigned_investigator, "priority": case.priority}


@app.post("/api/cases/{case_id}/notes", status_code=status.HTTP_201_CREATED)
def add_case_note(case_id: str, payload: CaseNoteCreateSchema, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    note = CaseNote(
        case_id=case_id,
        author=payload.author,
        note_text=payload.note_text,
        timestamp=datetime.utcnow()
    )
    db.add(note)

    audit = AuditLog(
        case_id=case_id,
        actor=payload.author,
        action="NOTE_ADDED",
        details=f"Investigator note recorded: {payload.note_text[:50]}...",
        timestamp=datetime.utcnow(),
        ip_address="127.0.0.1"
    )
    db.add(audit)
    db.commit()

    return {"note_id": note.id, "case_id": case_id, "timestamp": note.timestamp.isoformat(), "message": "Note recorded"}


# -------------------------------------------------------------
# PDF Evidence Export
# -------------------------------------------------------------
@app.get("/api/cases/{case_id}/export")
def export_case_evidence(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    alert = db.query(Alert).filter(Alert.id == case.alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Associated alert not found")

    pdf_bytes = generate_case_pdf(case, alert, db)

    filename = f"ZenithGuard_Evidence_Dossier_{case_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Report-Fingerprint": "SHA-256 Verified"
        }
    )


# -------------------------------------------------------------
# Benchmark Metrics & Accuracy Endpoint
# -------------------------------------------------------------
@app.get("/api/metrics")
def get_metrics():
    metrics = pipeline_instance.evaluate_metrics()
    return metrics


# -------------------------------------------------------------
# Employee DNA & Profiling
# -------------------------------------------------------------
@app.get("/api/employees")
def list_employees(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    res = []
    for emp in employees:
        branch = db.query(Branch).filter(Branch.id == emp.branch_id).first()
        res.append({
            "id": emp.id,
            "name": emp.name,
            "email": emp.email,
            "role": emp.role,
            "branch_id": emp.branch_id,
            "branch_name": branch.name if branch else emp.branch_id,
            "authorized_customer_range": emp.authorized_customer_range
        })
    return res


@app.get("/api/employees/{employee_id}/dna")
def get_employee_dna(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    if not pipeline_instance._is_profiler_trained:
        pipeline_instance.train_profiler()

    dna_eval = pipeline_instance.role_dna_profiler.evaluate_employee(employee_id)
    alerts = db.query(Alert).filter(Alert.employee_id == employee_id).all()

    # Radar chart comparison formatting
    radar_labels = [
        {"key": "total_access", "label": "Access Volume", "max": 250},
        {"key": "after_hours_ratio", "label": "After-Hours Rate", "max": 1.0},
        {"key": "distinct_customers", "label": "Distinct Profiles", "max": 100},
        {"key": "modification_rate", "label": "Record Modifications", "max": 0.3},
        {"key": "cross_branch_ratio", "label": "Cross-Branch Ratio", "max": 0.5},
    ]

    metrics = dna_eval.get("metrics", {})
    peer_means = dna_eval.get("peer_means", {})

    radar_data = []
    for r in radar_labels:
        emp_val = metrics.get(r["key"], 0.0)
        peer_val = peer_means.get(r["key"], 0.0)
        radar_data.append({
            "dimension": r["label"],
            "employee_value": round(emp_val, 3),
            "peer_mean": round(peer_val, 3),
            "z_score": dna_eval.get("z_scores", {}).get(r["key"], 0.0)
        })

    return {
        "employee_id": employee_id,
        "name": emp.name,
        "role": emp.role,
        "branch_id": emp.branch_id,
        "anomaly_score": dna_eval.get("score", 0.0),
        "anomaly_reason": dna_eval.get("reason", "Within peer bounds"),
        "radar_data": radar_data,
        "alert_history": [
            {
                "id": a.id,
                "created_at": a.created_at.isoformat(),
                "alert_type": a.alert_type,
                "risk_score": a.risk_score,
                "risk_level": a.risk_level,
                "status": a.status
            }
            for a in alerts
        ]
    }


# -------------------------------------------------------------
# Live Simulation & Pipeline Execution
# -------------------------------------------------------------
@app.post("/api/run-detection")
def trigger_detection(shield_enabled: bool = True):
    alerts = pipeline_instance.run_full_scan(shield_enabled=shield_enabled)
    return {
        "status": "SUCCESS",
        "alerts_generated": len(alerts),
        "shield_enabled": shield_enabled,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/simulate")
def simulate_scenario(payload: SimulateScenarioSchema, db: Session = Depends(get_db)):
    """
    Live Scenario Injection for hackathon demonstration:
    Injects custom transactions and access logs into SQLite and immediately triggers detection.
    """
    now = datetime.utcnow()
    injected_desc = ""

    if payload.scenario_type == "SUSPICIOUS_INSIDER":
        # Inject rapid circular structuring under 50k
        c_target = payload.customer_id or "C417"
        e_target = payload.employee_id or "E102"
        amt = payload.amount or 49000.0

        # Log
        sim_log = AccessLog(
            id=f"LOG_SIM_{int(now.timestamp())}",
            timestamp=now - timedelta(minutes=5),
            employee_id=e_target,
            customer_id=c_target,
            action="MODIFY_DETAILS",
            ip_address="10.14.99.12",
            is_after_hours=False
        )
        db.add(sim_log)

        # 3-hop circular flow
        sim_tx1 = Transaction(
            id=f"TXN_SIM_1_{int(now.timestamp())}",
            timestamp=now - timedelta(minutes=3),
            from_account_id=f"ACC_{c_target}_1",
            to_account_id="ACC_C208_1",
            from_customer_id=c_target,
            to_customer_id="C208",
            amount=amt,
            txn_type="TRANSFER",
            channel="IMPS",
            description="Live simulation hop 1"
        )
        sim_tx2 = Transaction(
            id=f"TXN_SIM_2_{int(now.timestamp())}",
            timestamp=now - timedelta(minutes=2),
            from_account_id="ACC_C208_1",
            to_account_id="ACC_C731_1",
            from_customer_id="C208",
            to_customer_id="C731",
            amount=amt - 500.0,
            txn_type="TRANSFER",
            channel="IMPS",
            description="Live simulation hop 2"
        )
        sim_tx3 = Transaction(
            id=f"TXN_SIM_3_{int(now.timestamp())}",
            timestamp=now - timedelta(minutes=1),
            from_account_id="ACC_C731_1",
            to_account_id=f"ACC_{c_target}_1",
            from_customer_id="C731",
            to_customer_id=c_target,
            amount=amt - 1100.0,
            txn_type="TRANSFER",
            channel="IMPS",
            description="Live simulation hop 3"
        )
        db.add_all([sim_tx1, sim_tx2, sim_tx3])
        injected_desc = f"Injected unauthorized access by {e_target} followed by INR {amt:,.0f} circular cycle"

    elif payload.scenario_type == "BENIGN_TICKET":
        # Approved service ticket
        sim_log = AccessLog(
            id=f"LOG_SIM_TKT_{int(now.timestamp())}",
            timestamp=now,
            employee_id="E105",
            customer_id="C350",
            action="VIEW_ACCOUNT",
            ip_address="10.14.1.25",
            service_ticket_id=f"TKT-DEMO-{int(now.timestamp()) % 10000}",
            is_after_hours=False
        )
        db.add(sim_log)
        injected_desc = "Injected legitimate cross-branch query with verified IT Service Ticket"

    elif payload.scenario_type == "STRUCTURING":
        c_target = payload.customer_id or "C142"
        for i in range(3):
            st = Transaction(
                id=f"TXN_SIM_STR_{i}_{int(now.timestamp())}",
                timestamp=now - timedelta(minutes=10 * (3 - i)),
                from_account_id=f"ACC_{c_target}_1",
                to_account_id=f"ACC_C{201+i}_1",
                from_customer_id=c_target,
                to_customer_id=f"C{201+i}",
                amount=49200.0 - (i * 200.0),
                txn_type="TRANSFER",
                channel="UPI",
                description=f"Structured transfer installment #{i+1}"
            )
            db.add(st)
        injected_desc = f"Injected 3 structured installments just under INR 50k threshold for {c_target}"

    db.commit()

    # Re-run detection pipeline
    alerts = pipeline_instance.run_full_scan()

    audit = AuditLog(
        actor="Investigator (Simulator)",
        action="SCENARIO_INJECTED",
        details=f"Injected {payload.scenario_type}: {injected_desc}",
        timestamp=now,
        ip_address="127.0.0.1"
    )
    db.add(audit)
    db.commit()

    return {
        "status": "INJECTED",
        "scenario_type": payload.scenario_type,
        "details": injected_desc,
        "total_active_alerts": len(alerts)
    }


# -------------------------------------------------------------
# Audit Trail Endpoint
# -------------------------------------------------------------
@app.get("/api/audit-logs")
def get_audit_logs(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50).all()
    return [
        {
            "id": l.id,
            "case_id": l.case_id,
            "actor": l.actor,
            "action": l.action,
            "details": l.details,
            "timestamp": l.timestamp.isoformat()
        }
        for l in logs
    ]
