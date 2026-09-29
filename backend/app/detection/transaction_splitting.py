from typing import Dict, Any, List
from datetime import timedelta
from backend.data.models import Transaction


def detect_transaction_splitting(
    transactions: List[Transaction],
    customer_id: str,
    threshold: float = 50000.0,
    lower_ratio: float = 0.90,
    upper_ratio: float = 0.999,
    window_hours: int = 24,
    min_count: int = 3
) -> Dict[str, Any]:
    """
    Detects smurfing/structuring patterns where transactions cluster just below statutory thresholds.
    """
    if not transactions:
        return {"score": 0.0, "evidence": [], "reason": "No transactions to evaluate"}

    lower_bound = threshold * lower_ratio
    upper_bound = threshold * upper_ratio

    # Filter transactions involving the target customer within structuring band
    structured_txns = [
        t for t in transactions
        if (t.from_customer_id == customer_id or t.to_customer_id == customer_id)
        and lower_bound <= t.amount <= upper_bound
    ]

    if not structured_txns:
        return {
            "signal": "transaction_splitting",
            "score": 0.0,
            "evidence": [],
            "reason": "No structured transactions detected near reporting threshold",
            "count": 0,
            "total_structured_amount": 0.0
        }

    # Group into time windows of window_hours
    structured_txns.sort(key=lambda t: t.timestamp)
    best_cluster = []
    
    for i in range(len(structured_txns)):
        t_start = structured_txns[i].timestamp
        t_end = t_start + timedelta(hours=window_hours)
        cluster = [t for t in structured_txns[i:] if t.timestamp <= t_end]
        if len(cluster) > len(best_cluster):
            best_cluster = cluster

    count = len(best_cluster)
    if count < 2:
        return {
            "signal": "transaction_splitting",
            "score": 0.0,
            "evidence": [],
            "reason": "Isolated transaction near threshold; insufficient evidence of structuring",
            "count": count,
            "total_structured_amount": 0.0
        }

    total_amount = sum(t.amount for t in best_cluster)
    evidence_ids = [t.id for t in best_cluster]

    # Calculate score based on count
    # 2 txns: 0.65, 3 txns: 0.85, 4+ txns: 0.95
    if count >= 4:
        score = 0.95
    elif count == 3:
        score = 0.85
    else:
        score = 0.65

    reason = (
        f"Detected {count} structured transactions between ₹{lower_bound:,.0f} and ₹{upper_bound:,.0f} "
        f"(totaling ₹{total_amount:,.0f}) just under ₹{threshold:,.0f} threshold within {window_hours}h window"
    )

    return {
        "signal": "transaction_splitting",
        "score": score,
        "evidence": evidence_ids,
        "reason": reason,
        "count": count,
        "total_structured_amount": total_amount,
        "threshold": threshold
    }
