# app/nlp_engine/intent_classifier/rule_based.py

def classify(query: str):
    query = query.lower()

    if "total" in query or "sum" in query:
        return "sum"

    if "average" in query or "avg" in query:
        return "average"

    if "count" in query:
        return "count"

    if "compare" in query or "vs" in query:
        return {
            "intent": "comparison",
            "comparison": "previous_period"
        }

    if "why" in query or "reason" in query:
        return {
            "intent": "diagnostic"
        }

    return "unknown"