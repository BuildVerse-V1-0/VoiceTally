# app/nlp_engine/semantic_router.py

def route_query(intent_data):

    # If dict intent
    if isinstance(intent_data, dict):

        intent = intent_data.get("intent")

        if intent == "comparison":
            return "comparison"

        if intent == "diagnostic":
            return "insights"

    # If string intent
    if intent_data in ["sum", "average", "count"]:
        return "aggregation"

    # 🔥 DEFAULT → aggregation (VERY IMPORTANT)
    return "aggregation"