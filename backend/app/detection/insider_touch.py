from typing import Dict, Any, List, Optional
from datetime import timedelta
from backend.data.models import AccessLog, Transaction, Employee, Customer


def detect_insider_touch(
    transactions: List[Transaction],
    access_logs: List[AccessLog],
    involved_customers: List[str],
    employees_map: Dict[str, Employee],
    customers_map: Dict[str, Customer],
    window_minutes: int = 30
) -> Dict[str, Any]:
    """
    Core Innovation: Quantifies temporal and behavioral correlation between insider telemetry
    and customer transaction execution.
    Score = f(access legitimacy, lag between access and first transfer, whether details were modified).
    """
    if not transactions or not access_logs or not involved_customers:
        return {
            "signal": "insider_touch",
            "score": 0.0,
            "evidence": [],
            "reason": "Insufficient transaction or telemetry data to evaluate insider touch",
            "lag_minutes": None,
            "details_modified": False,
            "is_unauthorized": False,
            "employee_id": None
        }

    # Earliest transaction timestamp
    txns_sorted = sorted(transactions, key=lambda t: t.timestamp)
    first_txn = txns_sorted[0]
    t0 = first_txn.timestamp

    # Look for access logs on any involved customer within window [t0 - window_minutes, t0 + 2 minutes]
    t_start = t0 - timedelta(minutes=window_minutes)
    t_end = t0 + timedelta(minutes=2)

    relevant_logs = [
        log for log in access_logs
        if log.customer_id in involved_customers
        and t_start <= log.timestamp <= t_end
    ]

    if not relevant_logs:
        # Check slightly wider window up to 60 min
        wider_logs = [
            log for log in access_logs
            if log.customer_id in involved_customers
            and (t0 - timedelta(minutes=60)) <= log.timestamp <= t_end
        ]
        if not wider_logs:
            return {
                "signal": "insider_touch",
                "score": 0.0,
                "evidence": [],
                "reason": f"No employee access records on involved accounts within {window_minutes}m before first transfer",
                "lag_minutes": None,
                "details_modified": False,
                "is_unauthorized": False,
                "employee_id": None
            }
        relevant_logs = wider_logs

    # Sort logs by time
    relevant_logs.sort(key=lambda l: l.timestamp)
    earliest_log = relevant_logs[0]

    # Calculate lag in minutes
    delta_seconds = (first_txn.timestamp - earliest_log.timestamp).total_seconds()
    lag_minutes = max(0.0, round(delta_seconds / 60.0, 1))

    # Identify primary employee
    emp_id = earliest_log.employee_id
    emp = employees_map.get(emp_id)
    cust = customers_map.get(earliest_log.customer_id)

    # Check legitimacy (unauthorized branch/customer range)
    is_unauthorized = False
    if emp and cust:
        if emp.branch_id != cust.home_branch_id:
            is_unauthorized = True
        elif emp.authorized_customer_range and "-" in emp.authorized_customer_range:
            try:
                s_num = int(emp.authorized_customer_range.split("-")[0].replace("C", ""))
                e_num = int(emp.authorized_customer_range.split("-")[1].replace("C", ""))
                c_num = int(cust.id.replace("C", ""))
                if c_num < s_num or c_num > e_num:
                    is_unauthorized = True
            except ValueError:
                pass

    # Check if details were modified
    details_modified = any(log.action == "MODIFY_DETAILS" for log in relevant_logs)

    # Compute Insider-Touch Score
    score = 0.0

    # 1. Temporal Proximity Factor (up to 0.40)
    if lag_minutes <= 5.0:
        score += 0.40
    elif lag_minutes <= 10.0:
        score += 0.30
    elif lag_minutes <= 20.0:
        score += 0.20
    else:
        score += 0.10

    # 2. Authorization Factor (up to 0.35)
    if is_unauthorized:
        score += 0.35
    else:
        score += 0.05

    # 3. Alteration / Modification Factor (up to 0.25)
    if details_modified:
        score += 0.25

    normalized_score = min(1.0, round(score, 2))

    reasons = []
    emp_name = emp.name if emp else emp_id
    cust_id = earliest_log.customer_id

    reasons.append(
        f"Insider Touch: Employee {emp_name} ({emp_id}) accessed {cust_id} only {lag_minutes:.0f} mins "
        f"prior to transaction inception ({first_txn.id}, ₹{first_txn.amount:,.0f})"
    )
    if is_unauthorized:
        reasons.append(f"Employee {emp_id} is unauthorized for customer {cust_id} (cross-branch access)")
    if details_modified:
        reasons.append(f"Customer details were modified (MODIFY_DETAILS) immediately preceding money movement")

    return {
        "signal": "insider_touch",
        "score": normalized_score,
        "evidence": [l.id for l in relevant_logs] + [first_txn.id],
        "reason": "; ".join(reasons),
        "lag_minutes": lag_minutes,
        "is_unauthorized": is_unauthorized,
        "details_modified": details_modified,
        "employee_id": emp_id,
        "customer_id": cust_id,
        "first_access_time": earliest_log.timestamp.isoformat(),
        "first_txn_time": first_txn.timestamp.isoformat(),
    }
