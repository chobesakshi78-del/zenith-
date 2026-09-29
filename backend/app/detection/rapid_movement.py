from typing import Dict, Any, List
from datetime import timedelta
from backend.data.models import Transaction


def detect_rapid_movement(
    transactions: List[Transaction],
    customer_id: str,
    max_lag_minutes: int = 15,
    min_preservation_ratio: float = 0.90
) -> Dict[str, Any]:
    """
    Detects rapid pass-through / funnel accounts where incoming funds are forwarded
    outward within minutes with minimal reduction.
    """
    if not transactions:
        return {"score": 0.0, "evidence": [], "reason": "No transactions to evaluate"}

    # Separate inbound and outbound for the target customer
    inbound = [t for t in transactions if t.to_customer_id == customer_id and t.amount >= 30000]
    outbound = [t for t in transactions if t.from_customer_id == customer_id and t.amount >= 30000]

    if not inbound or not outbound:
        return {
            "signal": "rapid_movement",
            "score": 0.0,
            "evidence": [],
            "reason": "No rapid pass-through or matched inbound/outbound flows observed"
        }

    matches = []
    for t_in in inbound:
        for t_out in outbound:
            if t_out.timestamp >= t_in.timestamp:
                delta_sec = (t_out.timestamp - t_in.timestamp).total_seconds()
                delta_min = delta_sec / 60.0
                if delta_min <= max_lag_minutes:
                    preservation = t_out.amount / t_in.amount
                    if min_preservation_ratio <= preservation <= 1.05:  # within 90% - 105%
                        matches.append({
                            "inbound": t_in,
                            "outbound": t_out,
                            "lag_minutes": delta_min,
                            "preservation": preservation
                        })

    if not matches:
        return {
            "signal": "rapid_movement",
            "score": 0.0,
            "evidence": [],
            "reason": "No matched rapid fund forwarding within timeframe"
        }

    # Best rapid match
    best = min(matches, key=lambda m: m["lag_minutes"])
    lag = best["lag_minutes"]
    preservation = best["preservation"]
    in_t = best["inbound"]
    out_t = best["outbound"]

    # Score: <5 mins -> 0.95, <10 mins -> 0.85, <15 mins -> 0.70
    if lag <= 5:
        score = 0.95
    elif lag <= 10:
        score = 0.85
    else:
        score = 0.70

    reason = (
        f"Rapid pass-through: Inbound ₹{in_t.amount:,.0f} forwarded as ₹{out_t.amount:,.0f} "
        f"({preservation*100:.1f}% preserved) in {lag:.1f} minutes to {out_t.to_customer_id}"
    )

    return {
        "signal": "rapid_movement",
        "score": score,
        "evidence": [in_t.id, out_t.id],
        "reason": reason,
        "lag_minutes": round(lag, 1),
        "preservation_ratio": round(preservation, 3)
    }
