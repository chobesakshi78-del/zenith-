from typing import Dict, Any, List
from backend.data.models import Employee, Customer, AccessLog


def detect_access_mismatch(
    employee: Employee,
    customer: Customer,
    access_logs: List[AccessLog]
) -> Dict[str, Any]:
    """
    Detects if an employee accessed a customer outside their authorized branch or customer range.
    """
    if not employee or not customer:
        return {"score": 0.0, "evidence": [], "reason": "No employee/customer record to evaluate"}

    evidence = []
    reasons = []
    score = 0.0

    # 1. Branch mismatch check
    is_branch_mismatch = (employee.branch_id != customer.home_branch_id)
    if is_branch_mismatch:
        score += 0.65
        reasons.append(
            f"Employee {employee.name} ({employee.id}, {employee.branch_id}) accessed customer {customer.name} "
            f"({customer.id}) belonging to unauthorized branch ({customer.home_branch_id})"
        )

    # 2. Customer ID range check
    range_str = employee.authorized_customer_range or ""
    if "-" in range_str:
        start_c, end_c = range_str.split("-")
        try:
            start_num = int(start_c.replace("C", ""))
            end_num = int(end_c.replace("C", ""))
            cust_num = int(customer.id.replace("C", ""))
            if cust_num < start_num or cust_num > end_num:
                score += 0.35
                reasons.append(
                    f"Customer {customer.id} is outside employee's authorized range [{employee.authorized_customer_range}]"
                )
        except ValueError:
            pass

    # Gather matching access logs
    for log in access_logs:
        if log.employee_id == employee.id and log.customer_id == customer.id:
            evidence.append(log.id)

    normalized_score = min(round(score, 2), 1.0)
    lead_reason = "; ".join(reasons) if reasons else "Access is within employee's authorized branch and portfolio"

    return {
        "signal": "access_mismatch",
        "score": normalized_score,
        "evidence": evidence,
        "reason": lead_reason,
        "is_unauthorized": (normalized_score >= 0.5)
    }
