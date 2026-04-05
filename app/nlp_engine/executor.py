# nlp_engine/executor.py

def execute_query(structured_query):

    # MOCK EXECUTION (replace with real DB later)

    if structured_query["type"] == "aggregation":
        return {
            "value": 125000,
            "unit": "INR"
        }

    elif structured_query["type"] == "comparison":
        return {
            "current": 150000,
            "previous": 130000,
            "growth": "15%"
        }

    elif structured_query["type"] == "insight":
        return {
            "trend": "decline",
            "reason": "drop in March sales"
        }

    return {}