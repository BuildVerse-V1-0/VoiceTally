# app/nlp_engine/intent_classifier/rule_based.py

def classify(query: str):

    query = query.lower()

    # Greeting
    if any(word in query for word in ["hi", "hello", "hey"]):
        return "greeting"

    # 🔥 FORECAST / FUTURE
    if any(word in query for word in [
        "forecast", "project", "future", "next", "upcoming"
    ]):
        return {"intent": "forecast"}

    # Aggregation
    if any(word in query for word in [
        "sales", "revenue", "income", "earn", "performance"
    ]):
        return "sum"

    # Comparison
    if any(word in query for word in ["compare", "vs", "difference"]):
        return {"intent": "comparison"}

    # Insight
    if any(word in query for word in ["why", "reason", "drop", "increase"]):
        return {"intent": "diagnostic"}

    return "unknown"