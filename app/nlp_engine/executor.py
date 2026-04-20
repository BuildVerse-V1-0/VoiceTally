# app/nlp_engine/executor.py

def execute_query(query_obj):

    metric = query_obj.get("metric", ["sales"])[0]
    time = query_obj.get("time")

    # 🔥 DIFFERENT VALUES BASED ON METRIC
    if metric == "sales":
        base = 125000
    elif metric == "revenue":
        base = 180000
    elif metric == "profit":
        base = 50000
    else:
        base = 100000

    # 🔥 MODIFY BY TIME
    if time == "last_month":
        value = base
    elif time == "last_2_months":
        value = base * 2
    elif time == "last_3_months":
        value = base * 3
    elif time == "last_quarter":
        value = base * 3
    else:
        value = base

    # 🔥 RESPONSE TYPES
    if query_obj["type"] == "aggregation":
        return {"value": value}

    if query_obj["type"] == "comparison":
        return {
            "current": value,
            "previous": int(value * 0.8),
            "growth": "20%"
        }

    if query_obj["type"] == "insight":
        return {
            "trend": "decline",
            "reason": "reduced demand"
        }

    return {}