"""组合贷：商业 + 公积金两腿各自等额本息，按期合并。

- validate_legs：缺腿或本金非正则拒绝（ValueError）。
- combo_schedule：回包分腿月供、合并月供、利息合计与合并预览；
  短腿还清后，该腿在合并行中当期记零。
"""
from app.engines.amortization import equal_payment_schedule

COMMERCIAL = "commercial"
FUND = "fund"
LEG_KEYS = (COMMERCIAL, FUND)
MAX_MONTHS = 600


def validate_legs(legs):
    """校验两腿齐全且参数合法；不合法抛 ValueError。"""
    if not isinstance(legs, dict):
        raise ValueError("legs")
    for key in LEG_KEYS:
        leg = legs.get(key)
        if not isinstance(leg, dict):
            raise ValueError(f"missing leg: {key}")
        try:
            principal = float(leg.get("principal"))
        except (TypeError, ValueError):
            raise ValueError(f"{key}.principal")
        if principal <= 0:
            raise ValueError(f"{key}.principal")
        try:
            rate = float(leg.get("annual_rate"))
        except (TypeError, ValueError):
            raise ValueError(f"{key}.annual_rate")
        if rate < 0:
            raise ValueError(f"{key}.annual_rate")
        try:
            months = int(leg.get("months"))
        except (TypeError, ValueError):
            raise ValueError(f"{key}.months")
        if months <= 0 or months > MAX_MONTHS:
            raise ValueError(f"{key}.months")


def _leg_row(schedule, i):
    """第 i 期（0 基）该腿行；短腿还清后返回零行。"""
    rows = schedule["rows"]
    if i < len(rows):
        return rows[i]
    return {"period": i + 1, "payment": 0.0, "principal": 0.0, "interest": 0.0, "balance": 0.0}


def combo_schedule(legs, preview_rows=12):
    """两腿分别等额本息后按期合并，返回回包。"""
    validate_legs(legs)
    per_leg = {}
    for key in LEG_KEYS:
        leg = legs[key]
        per_leg[key] = equal_payment_schedule(leg["principal"], leg["annual_rate"], leg["months"])
    n = max(len(per_leg[k]["rows"]) for k in LEG_KEYS)
    rows = []
    for i in range(n):
        c = _leg_row(per_leg[COMMERCIAL], i)
        f = _leg_row(per_leg[FUND], i)
        rows.append({
            "period": i + 1,
            "commercial_payment": c["payment"],
            "fund_payment": f["payment"],
            "payment": round(c["payment"] + f["payment"], 2),
            "principal": round(c["principal"] + f["principal"], 2),
            "interest": round(c["interest"] + f["interest"], 2),
            "balance": round(c["balance"] + f["balance"], 2),
        })
    return {
        "legs": {
            k: {
                "monthly_payment": per_leg[k]["monthly_payment"],
                "total_interest": per_leg[k]["total_interest"],
                "months": len(per_leg[k]["rows"]),
            }
            for k in LEG_KEYS
        },
        "monthly_payment": round(per_leg[COMMERCIAL]["monthly_payment"] + per_leg[FUND]["monthly_payment"], 2),
        "total_interest": round(per_leg[COMMERCIAL]["total_interest"] + per_leg[FUND]["total_interest"], 2),
        "total_payment": round(per_leg[COMMERCIAL]["total_payment"] + per_leg[FUND]["total_payment"], 2),
        "preview": rows[:preview_rows],
        "row_count": n,
    }
