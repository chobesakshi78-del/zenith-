from datetime import datetime, timedelta
import pytest
from backend.data.models import Transaction, AccessLog, Employee, Customer
from backend.app.detection.circular_flow import detect_circular_flow
from backend.app.detection.transaction_splitting import detect_transaction_splitting
from backend.app.detection.insider_touch import detect_insider_touch
from backend.app.detection.fusion import fuse_signals


def test_circular_flow_detected():
    base_t = datetime(2026, 9, 28, 10, 0, 0)
    txns = [
        Transaction(id="T1", timestamp=base_t, from_account_id="A1", to_account_id="A2", from_customer_id="C417", to_customer_id="C208", amount=49000.0),
        Transaction(id="T2", timestamp=base_t + timedelta(minutes=3), from_account_id="A2", to_account_id="A3", from_customer_id="C208", to_customer_id="C731", amount=48500.0),
        Transaction(id="T3", timestamp=base_t + timedelta(minutes=7), from_account_id="A3", to_account_id="A1", from_customer_id="C731", to_customer_id="C417", amount=47900.0),
    ]

    res = detect_circular_flow(txns, target_customer_id="C417", max_cycle_length=5)
    assert res["score"] >= 0.80
    assert len(res["evidence"]) == 3
    assert "C417" in res["cycle_path"]


def test_transaction_splitting():
    base_t = datetime(2026, 9, 28, 11, 0, 0)
    txns = [
        Transaction(id="TS1", timestamp=base_t, from_account_id="A1", to_account_id="A2", from_customer_id="C142", to_customer_id="C201", amount=49200.0),
        Transaction(id="TS2", timestamp=base_t + timedelta(minutes=30), from_account_id="A1", to_account_id="A3", from_customer_id="C142", to_customer_id="C202", amount=49100.0),
        Transaction(id="TS3", timestamp=base_t + timedelta(minutes=60), from_account_id="A1", to_account_id="A4", from_customer_id="C142", to_customer_id="C203", amount=48900.0),
    ]

    res = detect_transaction_splitting(txns, customer_id="C142", threshold=50000.0)
    assert res["score"] >= 0.80
    assert res["count"] == 3
    assert len(res["evidence"]) == 3


def test_insider_touch():
    t_log = datetime(2026, 9, 28, 10, 0, 0)
    t_txn = datetime(2026, 9, 28, 10, 5, 0)  # 5 min lag

    logs = [
        AccessLog(id="L1", timestamp=t_log, employee_id="E102", customer_id="C417", action="VIEW_ACCOUNT"),
        AccessLog(id="L2", timestamp=t_log + timedelta(minutes=1), employee_id="E102", customer_id="C417", action="MODIFY_DETAILS"),
    ]
    txns = [
        Transaction(id="TX1", timestamp=t_txn, from_account_id="A1", to_account_id="A2", from_customer_id="C417", to_customer_id="C208", amount=49000.0)
    ]

    emp = Employee(id="E102", name="Anil", email="anil@bank.com", role="CSO", branch_id="BR_PUNE", authorized_customer_range="C100-C180")
    cust = Customer(id="C417", name="Kavita", phone="999", email="k@bank.com", home_branch_id="BR_MUMBAI")

    res = detect_insider_touch(
        transactions=txns,
        access_logs=logs,
        involved_customers=["C417", "C208"],
        employees_map={"E102": emp},
        customers_map={"C417": cust},
        window_minutes=30
    )

    assert res["score"] >= 0.80
    assert res["lag_minutes"] == 5.0
    assert res["is_unauthorized"] is True
    assert res["details_modified"] is True


def test_fusion_and_shield():
    signals = {
        "access_mismatch": {"score": 0.9, "reason": "Unauthorized branch access"},
        "circular_flow": {"score": 0.95, "reason": "3-node circular loop"},
        "insider_touch": {"score": 0.9, "lag_minutes": 5.0, "reason": "5 min lag with modification"},
        "transaction_splitting": {"score": 0.8, "reason": "Sub-threshold structuring"},
        "false_positive_shield": {"score": 0.0, "reason": "None"}
    }

    # High risk without shield
    res_high = fuse_signals(signals, shield_enabled=True)
    assert res_high["risk_score"] >= 70.0
    assert res_high["risk_level"] == "High"
    assert res_high["boost_applied"] is True

    # Benign context with shield reduction
    signals_benign = {
        "access_mismatch": {"score": 0.6, "reason": "Cross-branch"},
        "false_positive_shield": {"score": -0.65, "reason": "Approved ticket TKT-8921"}
    }
    res_benign = fuse_signals(signals_benign, shield_enabled=True)
    assert res_benign["risk_score"] < 40.0
    assert res_benign["risk_level"] == "Low"
    assert res_benign["shield_applied"] is True
