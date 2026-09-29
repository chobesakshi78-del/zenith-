from typing import Dict, Any, List
from backend.app.detection.fusion import fuse_signals


def generate_explanation(
    signals: Dict[str, Dict[str, Any]],
    fusion_result: Dict[str, Any],
    employee_name: str = "Employee",
    employee_id: str = "E100",
    customer_id: str = "C100",
    customer_name: str = "Customer",
    similar_cases_count: int = 0
) -> Dict[str, Any]:
    """
    Generates multi-layered explainability for investigator decision support:
      (a) Signal contribution breakdown with one-line rationale
      (b) Synthesized plain-English narrative paragraph
      (c) Mathematical counterfactual inference via active re-fusion
      (d) Similar historical precedent case matching
    """
    contributions = fusion_result.get("contributions", [])
    current_score = fusion_result.get("risk_score", 0.0)

    # 1. Plain English Narrative Synthesizer
    narrative_parts = []
    
    # Check top signals
    top_signals = [c for c in contributions if c["raw_score"] > 0]
    
    insider_sig = signals.get("insider_touch", {})
    mismatch_sig = signals.get("access_mismatch", {})
    circular_sig = signals.get("circular_flow", {})
    split_sig = signals.get("transaction_splitting", {})
    rapid_sig = signals.get("rapid_movement", {})
    dna_sig = signals.get("role_dna_anomaly", {})
    shield_sig = signals.get("false_positive_shield", {})

    lead_lines = []
    
    if mismatch_sig.get("score", 0) > 0 and insider_sig.get("score", 0) > 0:
        lag_val = insider_sig.get("lag_minutes", 0)
        mod_note = " Customer credentials/details were altered prior to transactions." if insider_sig.get("details_modified") else ""
        lead_lines.append(
            f"Employee {employee_name} ({employee_id}) performed an unauthorized lookup on {customer_name} ({customer_id}) "
            f"located outside authorized branch limits.{mod_note} Approximately {lag_val:.0f} minutes later (Insider-Touch Lag), "
            f"high-velocity transaction activity commenced on the account."
        )
    elif mismatch_sig.get("score", 0) > 0:
        lead_lines.append(
            f"Employee {employee_name} ({employee_id}) accessed customer {customer_name} ({customer_id}) "
            f"in violation of branch-level access control boundaries."
        )

    if circular_sig.get("score", 0) > 0:
        cycle_path = " → ".join(circular_sig.get("cycle_path", [])) if circular_sig.get("cycle_path") else "a circular ring"
        lead_lines.append(
            f"Funds were routed in a closed circular loop ({cycle_path}) within {circular_sig.get('duration_minutes', 0):.0f} minutes "
            f"preserving {circular_sig.get('amount_retention', 0)*100:.1f}% of capital, indicative of synthetic volume generation or layering."
        )

    if split_sig.get("score", 0) > 0:
        lead_lines.append(
            f"Transactions were intentionally structured ({split_sig.get('count', 0)} installments) "
            f"clustered between 90% and 99.9% of the ₹50,000 regulatory reporting threshold."
        )

    if rapid_sig.get("score", 0) > 0 and not circular_sig.get("score", 0) > 0:
        lead_lines.append(
            f"Pass-through velocity was detected with funds forwarded within {rapid_sig.get('lag_minutes', 0):.1f} minutes of receipt."
        )

    if dna_sig.get("score", 0) >= 0.5:
        lead_lines.append(
            f"Behavioral profiling (Role-DNA) reveals an anomaly score of {dna_sig.get('score', 0):.2f}, "
            f"deviating significantly from peer cohort benchmarks."
        )

    if shield_sig.get("mitigation_applied"):
        lead_lines.append(
            f"False-Positive Shield applied a -{fusion_result.get('shield_adjustment_pct', 0):.0f}% dampening due to recognized legitimate context: "
            f"{shield_sig.get('reason')}."
        )

    if not lead_lines:
        narrative_paragraph = (
            f"Transaction and access activity for customer {customer_id} remains within normal parameters. "
            f"No critical anomalies were observed across insider telemetry or transaction graphs."
        )
    else:
        narrative_paragraph = " ".join(lead_lines)

    # 2. Counterfactual Simulation
    # Re-run fusion with key signals zeroed out to determine exact marginal impact
    counterfactual_lines = []

    # Counterfactual 1: What if employee was authorized? (access_mismatch = 0)
    if mismatch_sig.get("score", 0) > 0:
        cf_signals = {k: dict(v) for k, v in signals.items()}
        cf_signals["access_mismatch"] = {"score": 0.0}
        # If authorized, insider touch score is also reduced
        if "insider_touch" in cf_signals and cf_signals["insider_touch"].get("score", 0) > 0:
            it_copy = dict(cf_signals["insider_touch"])
            it_copy["score"] = max(0.2, it_copy["score"] - 0.35)
            cf_signals["insider_touch"] = it_copy
        cf_res = fuse_signals(cf_signals, shield_enabled=fusion_result.get("shield_applied", True))
        cf_score = cf_res["risk_score"]
        counterfactual_lines.append(
            f"If {customer_id} were in {employee_id}'s authorized customer portfolio, "
            f"the risk score would drop from {current_score:.0f} to {cf_score:.0f} ({cf_res['risk_level']})."
        )

    # Counterfactual 2: What if transactions were not circular?
    if circular_sig.get("score", 0) > 0:
        cf_signals = {k: dict(v) for k, v in signals.items()}
        cf_signals["circular_flow"] = {"score": 0.0}
        cf_res = fuse_signals(cf_signals, shield_enabled=fusion_result.get("shield_applied", True))
        cf_score = cf_res["risk_score"]
        counterfactual_lines.append(
            f"If the money flow did not complete a closed cycle, "
            f"the risk score would drop from {current_score:.0f} to {cf_score:.0f} ({cf_res['risk_level']})."
        )

    # Counterfactual 3: What if there was no insider touch?
    if insider_sig.get("score", 0) > 0 and not counterfactual_lines:
        cf_signals = {k: dict(v) for k, v in signals.items()}
        cf_signals["insider_touch"] = {"score": 0.0, "lag_minutes": None}
        cf_res = fuse_signals(cf_signals, shield_enabled=fusion_result.get("shield_applied", True))
        cf_score = cf_res["risk_score"]
        counterfactual_lines.append(
            f"Without employee access within 30 minutes prior to transactions, "
            f"the risk score would drop from {current_score:.0f} to {cf_score:.0f} ({cf_res['risk_level']})."
        )

    counterfactual_summary = counterfactual_lines[0] if counterfactual_lines else "Marginal sensitivity is uniform across current indicators."

    return {
        "contributions": contributions,
        "narrative": narrative_paragraph,
        "counterfactual": counterfactual_summary,
        "all_counterfactuals": counterfactual_lines,
        "similar_past_cases_count": similar_cases_count,
        "historical_precedent_note": (
            f"Identical behavioral and flow pattern detected in {similar_cases_count} previous incident{'s' if similar_cases_count != 1 else ''} "
            f"involving {employee_id}"
            if similar_cases_count > 0 else "First occurrence of this pattern by this employee"
        )
    }
