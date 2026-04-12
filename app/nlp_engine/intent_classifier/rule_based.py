# app/nlp_engine/intent_classifier/rule_based.py

def classify(query: str):

    query = query.lower()

    # Aggregation (default behavior)
    if any(word in query for word in [
        "total", "sum", "sales", "revenue", "income"
    ]):
        return "sum"

    # Average
    if any(word in query for word in [
        "average", "avg", "mean"
    ]):
        return "average"

    # Count
    if any(word in query for word in [
        "count", "how many", "number of"
    ]):
        return "count"

    # Comparison
    if any(word in query for word in [
        "compare", "vs", "versus", "difference"
    ]):
        return {"intent": "comparison"}

    # Insight
    if any(word in query for word in [
        "why", "reason", "cause", "drop", "increase"
    ]):
        return {"intent": "diagnostic"}

    # 🔥 Default (VERY IMPORTANT)
    return "sum"