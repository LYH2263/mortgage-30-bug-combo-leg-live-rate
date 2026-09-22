import pytest
from app.modules.combo_loan import combo_schedule, validate_legs

LEGS = {
    "commercial": {"principal": 600000, "annual_rate": 3.6, "months": 360},
    "fund": {"principal": 400000, "annual_rate": 3.1, "months": 240},
}

def test_monthly_payment_is_sum_of_legs():
    out = combo_schedule(LEGS)
    assert out["monthly_payment"] == round(
        out["legs"]["commercial"]["monthly_payment"] + out["legs"]["fund"]["monthly_payment"], 2)
    assert out["legs"]["commercial"]["months"] == 360
    assert out["legs"]["fund"]["months"] == 240

def test_total_interest_is_sum_of_legs():
    out = combo_schedule(LEGS)
    assert out["total_interest"] == round(
        out["legs"]["commercial"]["total_interest"] + out["legs"]["fund"]["total_interest"], 2)

def test_short_leg_zeroed_after_payoff():
    out = combo_schedule(LEGS, preview_rows=360)
    rows = out["preview"]
    assert out["row_count"] == 360
    # 公积金腿 240 期还清，之后当期记零；商业腿仍有月供
    assert rows[239]["fund_payment"] > 0
    assert rows[240]["fund_payment"] == 0.0
    assert rows[240]["commercial_payment"] > 0
    assert rows[240]["payment"] == rows[240]["commercial_payment"]

def test_first_period_merges_both_legs():
    out = combo_schedule(LEGS)
    first = out["preview"][0]
    assert first["period"] == 1
    assert first["payment"] == round(first["commercial_payment"] + first["fund_payment"], 2)

def test_missing_leg_rejected():
    with pytest.raises(ValueError):
        validate_legs({"commercial": LEGS["commercial"]})
    with pytest.raises(ValueError):
        combo_schedule({"fund": LEGS["fund"]})

def test_non_positive_principal_rejected():
    bad = {"commercial": {**LEGS["commercial"], "principal": 0}, "fund": LEGS["fund"]}
    with pytest.raises(ValueError):
        validate_legs(bad)
    neg = {"commercial": LEGS["commercial"], "fund": {**LEGS["fund"], "principal": -1}}
    with pytest.raises(ValueError):
        combo_schedule(neg)

def test_bad_months_rejected():
    with pytest.raises(ValueError):
        validate_legs({"commercial": {**LEGS["commercial"], "months": 0}, "fund": LEGS["fund"]})
