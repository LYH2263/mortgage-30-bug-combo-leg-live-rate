import json
from app.engines.amortization import equal_payment_schedule
from app.modules.combo_loan import COMMERCIAL, FUND, LEG_KEYS, _leg_row


def merge_with_live_commercial(stored_legs: dict, live_legs: dict, preview_rows: int = 12) -> dict:
    per_leg = {}
    for key in LEG_KEYS:
        leg = stored_legs[key] if key == FUND else live_legs.get(key) or stored_legs[key]
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


def stored_legs_from_run(row: dict) -> dict | None:
    try:
        return json.loads(row.get("input_json") or "null")
    except (TypeError, ValueError):
        return None
