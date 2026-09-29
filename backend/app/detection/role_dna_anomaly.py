from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from backend.data.models import Employee, AccessLog, Customer


class RoleDNAProfiler:
    def __init__(self):
        self.peer_stats = {}
        self.model = None
        self.feature_cols = [
            "total_access",
            "after_hours_ratio",
            "distinct_customers",
            "modification_rate",
            "cross_branch_ratio"
        ]

    def fit_cohorts(self, employees: List[Employee], access_logs: List[AccessLog], customers: List[Customer]):
        """
        Builds peer cohort profiles and fits IsolationForest for anomaly detection.
        """
        cust_branch_map = {c.id: c.home_branch_id for c in customers}
        emp_branch_map = {e.id: e.branch_id for e in employees}
        emp_role_map = {e.id: e.role for e in employees}

        rows = []
        for emp in employees:
            emp_logs = [log for log in access_logs if log.employee_id == emp.id]
            total = len(emp_logs)
            if total == 0:
                rows.append({
                    "employee_id": emp.id,
                    "role": emp.role,
                    "branch_id": emp.branch_id,
                    "total_access": 0,
                    "after_hours_ratio": 0.0,
                    "distinct_customers": 0,
                    "modification_rate": 0.0,
                    "cross_branch_ratio": 0.0,
                })
                continue

            after_hours = sum(1 for log in emp_logs if log.is_after_hours)
            distinct_c = len(set(log.customer_id for log in emp_logs if log.customer_id))
            modifications = sum(1 for log in emp_logs if log.action == "MODIFY_DETAILS")
            cross_branch = sum(
                1 for log in emp_logs
                if log.customer_id and cust_branch_map.get(log.customer_id) != emp.branch_id
            )

            rows.append({
                "employee_id": emp.id,
                "role": emp.role,
                "branch_id": emp.branch_id,
                "total_access": total,
                "after_hours_ratio": round(after_hours / total, 4),
                "distinct_customers": distinct_c,
                "modification_rate": round(modifications / total, 4),
                "cross_branch_ratio": round(cross_branch / total, 4),
            })

        df = pd.DataFrame(rows)
        self.df_metrics = df

        # Peer group means and standard deviations
        cohort_groups = df.groupby(["role", "branch_id"])
        self.cohort_means = cohort_groups[self.feature_cols].mean().to_dict(orient="index")
        self.cohort_stds = cohort_groups[self.feature_cols].std().fillna(1.0).to_dict(orient="index")
        self.overall_means = df[self.feature_cols].mean().to_dict()

        # Fit IsolationForest on numerical features
        X = df[self.feature_cols].values
        self.iso_forest = IsolationForest(contamination=0.10, random_state=42)
        self.iso_forest.fit(X)
        df["anomaly_score"] = -self.iso_forest.score_samples(X)

    def evaluate_employee(self, employee_id: str) -> Dict[str, Any]:
        """
        Calculates Role-DNA anomaly score, peer comparison metrics, and z-score breakdown.
        """
        if not hasattr(self, "df_metrics") or self.df_metrics is None:
            return {"score": 0.0, "evidence": [], "reason": "Model not fitted"}

        emp_row = self.df_metrics[self.df_metrics["employee_id"] == employee_id]
        if emp_row.empty:
            return {"score": 0.0, "evidence": [], "reason": f"No telemetry for employee {employee_id}"}

        row = emp_row.iloc[0]
        role = row["role"]
        branch_id = row["branch_id"]
        cohort_key = (role, branch_id)

        means = self.cohort_means.get(cohort_key, self.overall_means)
        stds = self.cohort_stds.get(cohort_key, {k: 1.0 for k in self.feature_cols})

        z_scores = {}
        high_z_reasons = []
        for col in self.feature_cols:
            mean_val = means.get(col, 0.0)
            std_val = stds.get(col, 1.0)
            if std_val == 0 or np.isnan(std_val):
                std_val = 1.0
            val = row[col]
            z = (val - mean_val) / std_val
            z_scores[col] = round(float(z), 2)
            if z >= 2.0:
                high_z_reasons.append(f"{col.replace('_', ' ').title()} is {z:.1f}σ above {role} cohort average")

        # Isolation forest raw score mapped to 0-1
        raw_iso = float(row["anomaly_score"])
        # Min-max scaling heuristic for IsolationForest score_samples (-0.65 to -0.35 typical)
        norm_iso = max(0.0, min(1.0, (raw_iso - 0.45) / 0.30))

        # Max z-score factor
        max_z = max(z_scores.values()) if z_scores else 0.0
        z_factor = max(0.0, min(1.0, max_z / 4.0))

        # Blended score
        combined_score = round(0.5 * norm_iso + 0.5 * z_factor, 2)
        if combined_score > 1.0:
            combined_score = 1.0

        reason = (
            "; ".join(high_z_reasons)
            if high_z_reasons
            else f"Behavioral patterns align within acceptable variance for {role} cohort"
        )

        return {
            "signal": "role_dna_anomaly",
            "score": combined_score,
            "evidence": [f"employee:{employee_id}", f"max_z:{max_z:.2f}"],
            "reason": reason,
            "z_scores": z_scores,
            "metrics": {col: float(row[col]) for col in self.feature_cols},
            "peer_means": {col: float(means.get(col, 0.0)) for col in self.feature_cols}
        }
