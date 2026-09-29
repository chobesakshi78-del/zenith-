from typing import Dict, Any, List, Set
from backend.data.models import AccessLog


def detect_collusion(
    involved_customers: List[str],
    access_logs: List[AccessLog]
) -> Dict[str, Any]:
    """
    Detects if multiple bank employees are repeatedly accessing the same cluster/ring of accounts.
    """
    if not involved_customers or len(involved_customers) < 2:
        return {"score": 0.0, "evidence": [], "reason": "Insufficient customer nodes for collusion analysis"}

    # Map customer -> set of employees who touched them
    cust_employees: Dict[str, Set[str]] = {cid: set() for cid in involved_customers}
    emp_touched_customers: Dict[str, Set[str]] = {}
    emp_log_ids: Dict[str, List[str]] = {}

    for log in access_logs:
        if log.customer_id in cust_employees and log.employee_id:
            cust_employees[log.customer_id].add(log.employee_id)
            if log.employee_id not in emp_touched_customers:
                emp_touched_customers[log.employee_id] = set()
                emp_log_ids[log.employee_id] = []
            emp_touched_customers[log.employee_id].add(log.customer_id)
            emp_log_ids[log.employee_id].append(log.id)

    # Check for employees that touch multiple accounts in the ring
    involved_active_emps = [
        emp_id for emp_id, custs in emp_touched_customers.items()
        if len(custs) >= 2 or (len(involved_customers) <= 3 and len(custs) >= 1)
    ]

    if len(involved_active_emps) >= 2:
        evidence = []
        for e in involved_active_emps[:3]:
            evidence.extend(emp_log_ids[e][:5])

        score = min(1.0, 0.65 + 0.15 * (len(involved_active_emps) - 2))
        emp_str = ", ".join(involved_active_emps)
        reason = (
            f"Collusion indicator: Multiple employees ({emp_str}) actively modified/viewed "
            f"overlapping accounts in this {len(involved_customers)}-node ring"
        )
        return {
            "signal": "collusion",
            "score": round(score, 2),
            "evidence": evidence,
            "reason": reason,
            "involved_employees": involved_active_emps
        }

    return {
        "signal": "collusion",
        "score": 0.0,
        "evidence": [],
        "reason": "Single or no employee touch detected across ring nodes; no multi-employee collusion",
        "involved_employees": involved_active_emps
    }
