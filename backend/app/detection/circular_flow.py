from typing import Dict, Any, List
from datetime import timedelta
from backend.data.models import Transaction


def detect_circular_flow(
    transactions: List[Transaction],
    target_customer_id: str = None,
    max_cycle_length: int = 5,
    window_hours: int = 48,
    amount_similarity_tol: float = 0.15
) -> Dict[str, Any]:
    """
    Detects closed circular flow loops involving target_customer_id of length <= max_cycle_length
    with forward chronological ordering and high amount preservation.
    """
    if not transactions or len(transactions) < 2 or not target_customer_id:
        return {"score": 0.0, "evidence": [], "reason": "Insufficient transactions for cycle detection"}

    # Initial candidate transactions originating from target_customer_id, prioritized by recent first
    outbound_from_target = [
        t for t in transactions
        if t.from_customer_id == target_customer_id and t.amount >= 10000
    ]
    outbound_from_target.sort(key=lambda t: t.timestamp, reverse=True)

    if not outbound_from_target:
        return {
            "signal": "circular_flow",
            "score": 0.0,
            "evidence": [],
            "reason": f"No significant outbound transfers from customer {target_customer_id}",
            "cycles": []
        }

    detected_cycles = []

    # For each outbound transaction, search for cycles returning to target within window and amount tolerance
    for t_init in outbound_from_target[:5]:  # limit to top 5 initial outbound
        base_amt = t_init.amount
        t_start = t_init.timestamp
        t_max = t_start + timedelta(hours=window_hours)

        # Pre-filter candidate transactions strictly by time window and amount tolerance
        cands = [
            t for t in transactions
            if t_start <= t.timestamp <= t_max
            and abs(t.amount - base_amt) / max(1.0, base_amt) <= amount_similarity_tol
        ]

        if len(cands) < 2:
            continue

        # Build local adjacency map for candidate transactions
        adj: Dict[str, List[Transaction]] = {}
        for t in cands:
            if t.from_customer_id not in adj:
                adj[t.from_customer_id] = []
            adj[t.from_customer_id].append(t)

        steps = 0

        # Bounded BFS/DFS with step guard
        def search(curr_node: str, path: List[Transaction], visited: List[str]):
            nonlocal steps
            steps += 1
            if steps > 100 or len(path) >= max_cycle_length:
                return

            last_time = path[-1].timestamp if path else t_start

            for nxt_t in adj.get(curr_node, []):
                if nxt_t.id in [p.id for p in path]:
                    continue
                if nxt_t.timestamp < last_time:
                    continue

                nxt_node = nxt_t.to_customer_id

                if nxt_node == target_customer_id and len(path) >= 1:
                    full_seq = path + [nxt_t]
                    node_path = visited + [nxt_node]
                    dur_min = (full_seq[-1].timestamp - full_seq[0].timestamp).total_seconds() / 60.0
                    amts = [t.amount for t in full_seq]
                    retention = min(amts) / max(amts)

                    detected_cycles.append({
                        "cycle": node_path[:-1],
                        "cycle_path": node_path,
                        "length": len(full_seq),
                        "transactions": full_seq,
                        "duration_minutes": round(dur_min, 1),
                        "amount_retention": round(retention, 3),
                        "avg_amount": round(sum(amts) / len(amts), 2)
                    })
                    return

                if nxt_node not in visited and len(path) < max_cycle_length - 1:
                    search(nxt_node, path + [nxt_t], visited + [nxt_node])

        search(t_init.to_customer_id, [t_init], [target_customer_id, t_init.to_customer_id])

    if not detected_cycles:
        return {
            "signal": "circular_flow",
            "score": 0.0,
            "evidence": [],
            "reason": "No closed circular transaction cycles identified",
            "cycles": []
        }

    best_cycle = max(
        detected_cycles,
        key=lambda c: (1.0 / max(1.0, c["duration_minutes"])) * c["amount_retention"]
    )

    duration_min = best_cycle["duration_minutes"]
    retention = best_cycle["amount_retention"]
    speed_factor = 1.0 if duration_min <= 20 else max(0.5, 1.0 - (duration_min / (window_hours * 60)))
    retention_factor = max(0.5, retention)
    score = min(1.0, round(0.5 * speed_factor + 0.5 * retention_factor, 2))

    cycle_nodes_str = " -> ".join(best_cycle["cycle_path"])
    evidence_ids = [t.id for t in best_cycle["transactions"]]

    reason = (
        f"Circular money flow detected: {cycle_nodes_str} completed in {duration_min:.0f} mins "
        f"with {retention*100:.1f}% amount retention (Avg: INR {best_cycle['avg_amount']:,.0f})"
    )

    return {
        "signal": "circular_flow",
        "score": score,
        "evidence": evidence_ids,
        "reason": reason,
        "cycle_path": best_cycle["cycle_path"],
        "duration_minutes": duration_min,
        "amount_retention": retention,
        "cycles": detected_cycles
    }
