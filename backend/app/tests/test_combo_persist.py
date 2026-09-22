import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="mortgage-combo-test-")

import pytest
from app import seed
from app.services.mortgage_service import MortgageService

LEGS = {
    "commercial": {"principal": 600000, "annual_rate": 3.6, "months": 360},
    "fund": {"principal": 400000, "annual_rate": 3.1, "months": 240},
}

def setup_module():
    seed.init_db()

def test_persist_false_writes_nothing():
    with MortgageService() as s:
        before = len(s.history(100))
        out = s.combo_schedule(LEGS, None, False)
        assert out["run_id"] is None
        assert out["legs"]["commercial"]["monthly_payment"] > 0
        assert len(s.history(100)) == before

def test_persist_true_stores_run_with_both_leg_payments():
    with MortgageService() as s:
        out = s.combo_schedule(LEGS, None, True)
        assert out["run_id"]
        rec = [h for h in s.history(100) if h["id"] == out["run_id"]][0]
        assert rec["kind"] == "combo_schedule"
        # 历史记录带回两腿月供
        assert rec["result"]["legs"]["commercial"]["monthly_payment"] == out["legs"]["commercial"]["monthly_payment"]
        assert rec["result"]["legs"]["fund"]["monthly_payment"] == out["legs"]["fund"]["monthly_payment"]
        assert rec["result"]["monthly_payment"] == out["monthly_payment"]

def test_old_record_not_dragged_by_later_leg_rate_change():
    with MortgageService() as s:
        out = s.combo_schedule(LEGS, None, True)
        rid = out["run_id"]
        changed = {"commercial": dict(LEGS["commercial"]), "fund": {**LEGS["fund"], "annual_rate": 9.9}}
        newer = s.combo_schedule(changed, None, True)
        assert newer["legs"]["fund"]["monthly_payment"] != out["legs"]["fund"]["monthly_payment"]
        rec = [h for h in s.history(100) if h["id"] == rid][0]
        # 旧条仍是当时的快照：输入与两腿月供都不变
        assert rec["input"]["fund"]["annual_rate"] == LEGS["fund"]["annual_rate"]
        assert rec["result"]["legs"]["fund"]["monthly_payment"] == out["legs"]["fund"]["monthly_payment"]
        assert rec["result"]["monthly_payment"] == out["monthly_payment"]

def test_legacy_loan_without_legs_stays_single():
    with MortgageService() as s:
        loan = s.loan(1)
        assert loan["legs"] is None
        out = s.schedule(loan["principal"], loan["annual_rate"], loan["months"], loan["id"], False)
        assert "legs" not in out

def test_save_legs_roundtrip_and_summary_columns():
    with MortgageService() as s:
        loan = s.save_legs(2, LEGS)
        assert loan["legs"]["fund"]["months"] == 240
        assert loan["principal"] == 1000000.0
        assert loan["months"] == 360
        again = s.loan(2)
        assert again["legs"] == LEGS

def test_save_legs_rejects_missing_leg_and_bad_principal():
    with MortgageService() as s:
        with pytest.raises(ValueError):
            s.save_legs(2, {"commercial": LEGS["commercial"]})
        with pytest.raises(ValueError):
            s.save_legs(2, {"commercial": {**LEGS["commercial"], "principal": 0}, "fund": LEGS["fund"]})
        assert s.save_legs(999, LEGS) is None
