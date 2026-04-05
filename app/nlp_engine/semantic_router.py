# nlp_engine/semantic_router.py

def route_query(intent_data):

    if isinstance(intent_data, dict):

        intent = intent_data.get("intent")

        if intent in ["sum", "average", "count"]:
            return "aggregation"

        elif intent == "comparison":
            return "comparison"

        elif intent == "diagnostic":
            return "insights"

    return "fallback"