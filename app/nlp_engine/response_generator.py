# app/nlp_engine/response_generator.py

def generate_response(query, structured, data):

    metric = structured.get("metric", ["data"])[0] if structured.get("metric") else "data"

    if structured["type"] == "aggregation":
        value = data.get("value", 0)
        return f"Your total {metric} is ₹{value}."

    if structured["type"] == "comparison":
        current = data.get("current", 0)
        previous = data.get("previous", 0)
        growth = data.get("growth", "0%")

        return (
            f"Your {metric} is ₹{current}, compared to ₹{previous} earlier. "
            f"This shows a growth of {growth}."
        )

    if structured["type"] == "insight":
        trend = data.get("trend", "stable")
        reason = data.get("reason", "no major changes")

        return f"Your {metric} shows a {trend}. This is likely due to {reason}."

    return "I processed your request, but couldn’t generate a clear insight."