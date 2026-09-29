from typing import Dict, Any, List
from datetime import timedelta
from backend.data.models import AccessLog


def detect_bulk_access(
    access_logs: List[AccessLog],
    employee_id: str,
    window_hours: int = 4,
    threshold_accounts: int = 15
) -> Dict[str, Any]:
    """
    Detects excessive or unusual-hour access patterns by an employee.
    """
    emp_logs = [log for log in access_logs if log.employee_id == employee_id and log.customer_id]
    if not emp_logs:
        return {"score": 0.0, "evidence": [], "reason": "No customer access logs for employee"}

    emp_logs.sort(key=lambda l: l.timestamp)

    # 1. Check for bulk queries within sliding window
    max_distinct_in_window = 0
    best_window_logs = []
    
    for i in range(len(emp_logs)):
        start_t = emp_logs[i].timestamp
        end_t = start_t + timedelta(hours=window_hours)
        window = [l for l in emp_logs[i:] if l.timestamp <= end_t]
        distinct = set(l.customer_id for l in window)
        if len(distinct) > max_distinct_in_window:
            max_distinct_in_window = len(distinct)
            best_window_logs = window

    # 2. Check after-hours concentration
    after_hours_count = sum(1 for l in emp_logs if l.is_after_hours)
    after_hours_ratio = after_hours_count / max(1, len(emp_logs))

    score = 0.0
    reasons = []

    if max_distinct_in_window >= threshold_accounts:
        bulk_score = min(1.0, 0.5 + (max_distinct_in_window / (threshold_accounts * 2)) * 0.5)
        score = max(score, bulk_score)
        reasons.append(
            f"Bulk access: {max_distinct_in_window} distinct customer records accessed within {window_hours}h"
        )

    if after_hours_count >= 10 or after_hours_ratio >= 0.40:
        score = max(score, 0.75 if after_hours_count >= 20 else 0.55)
        reasons.append(
            f"Unusual hours: {after_hours_count} access events recorded outside standard business hours"
        )

    if not reasons:
        return {
            "signal": "bulk_access",
            "score": 0.0,
            "evidence": [],
            "reason": "Customer access rate and operational hours are normal",
            "distinct_accounts_peak": max_distinct_in_window
        }

    evidence_ids = [l.id for l in best_window_logs[:10]]
    return {
        "signal": "bulk_access",
        "score": round(score, 2),
        "evidence": evidence_ids,
        "reason": "; ".join(reasons),
        "distinct_accounts_peak": max_distinct_in_window,
        "after_hours_count": after_hours_count
    }
