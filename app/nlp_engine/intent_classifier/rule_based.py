# app/nlp_engine/intent_classifier/rule_based.py

def classify(query: str):

    query = query.lower()

    # -------------------------------
    # AGGREGATION (MOST COMMON)
    # -------------------------------
    if any(word in query for word in [
        "total", "sum", "sales", "revenue", "income"
    ]):
        return "sum"

    # -------------------------------
    # AVERAGE
    # -------------------------------
    if any(word in query for word in [
        "average", "avg", "mean"
    ]):
        return "average"

    # -------------------------------
    # COUNT
    # -------------------------------
    if any(word in query for word in [
        "count", "how many", "number of"
    ]):
        return "count"

    # -------------------------------
    # COMPARISON
    # -------------------------------
    if any(word in query for word in [
        "compare", "vs", "versus", "difference"
    ]):
        return {"intent": "comparison"}

    # -------------------------------
    # INSIGHT / WHY
    # -------------------------------
    if any(word in query for word in [
        "why", "reason", "cause", "drop", "increase"
    ]):
        return {"intent": "diagnostic"}

    return "sum"  # 🔥 DEFAULT (IMPORTANT)