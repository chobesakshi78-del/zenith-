from typing import Dict, Any, List
from backend.app.detection.config import DETECTION_CONFIG


def fuse_signals(
    signals: Dict[str, Dict[str, Any]],
    weights: Dict[str, float] = None,
    shield_enabled: bool = True
) -> Dict[str, Any]:
    """
    Combines individual detector scores using probabilistic Noisy-OR,
    applies temporal Insider-Touch velocity boost, and executes False-Positive Shield dampening.
    Output:
      - risk_score: 0.0 - 100.0
      - risk_level: 'Low' (<40), 'Medium' (40-69), 'High' (>=70)
      - contributions: percentage contribution of each signal
    """
    if weights is None:
        weights = DETECTION_CONFIG["weights"]

    # 1. Base Noisy-OR: 1 - product(1 - w_i * s_i)
    prod_complement = 1.0
    signal_weights_applied = {}
    signal_raw_contributions = {}

    for sig_name, w in weights.items():
        sig_data = signals.get(sig_name, {})
        s_val = max(0.0, float(sig_data.get("score", 0.0)))
        effective_val = w * s_val
        signal_weights_applied[sig_name] = effective_val
        prod_complement *= (1.0 - effective_val)

    p_noisy_or = 1.0 - prod_complement

    # 2. Insider Touch Lag Boost
    insider_sig = signals.get("insider_touch", {})
    lag_min = insider_sig.get("lag_minutes")
    boost_applied = False
    boost_factor = 1.0

    if lag_min is not None and lag_min <= DETECTION_CONFIG["insider_touch_lag_boost_threshold_minutes"]:
        if insider_sig.get("score", 0) >= 0.5:
            boost_factor = DETECTION_CONFIG["insider_touch_lag_boost_multiplier"]
            p_noisy_or = min(0.99, p_noisy_or * boost_factor)
            boost_applied = True

    # 3. False-Positive Shield Adjustment
    shield_sig = signals.get("false_positive_shield", {})
    shield_adjustment = 0.0
    shield_score = float(shield_sig.get("score", 0.0))

    if shield_enabled and shield_score < 0:
        shield_adjustment = abs(shield_score)
        # Apply proportional dampening
        p_noisy_or = max(0.05, p_noisy_or * (1.0 - shield_adjustment))

    # 4. Final Risk Score (0 - 100)
    risk_score = round(p_noisy_or * 100.0, 1)

    # 5. Risk Level Categorization
    if risk_score >= 70.0:
        risk_level = "High"
    elif risk_score >= 40.0:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # 6. Contribution Breakdown Calculation
    # Compute relative share of log odds or effective values
    total_effective = sum(signal_weights_applied.values())
    contributions = []

    for sig_name, eff_val in signal_weights_applied.items():
        if total_effective > 0 and eff_val > 0:
            pct = round((eff_val / total_effective) * 100.0, 1)
        else:
            pct = 0.0

        sig_info = signals.get(sig_name, {})
        contributions.append({
            "signal": sig_name,
            "weight": weights.get(sig_name, 0.0),
            "raw_score": sig_info.get("score", 0.0),
            "effective_score": round(eff_val, 3),
            "contribution_pct": pct,
            "reason": sig_info.get("reason", "No anomaly detected")
        })

    # Sort descending by contribution
    contributions.sort(key=lambda c: c["contribution_pct"], reverse=True)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "raw_p": round(p_noisy_or, 4),
        "boost_applied": boost_applied,
        "shield_applied": (shield_adjustment > 0),
        "shield_adjustment_pct": round(shield_adjustment * 100, 1),
        "contributions": contributions
    }
