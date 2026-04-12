# app/nlp_engine/response_generator.py

def generate_response(query, structured, data):

    metric = structured.get("metric", ["sales"])[0]

    if structured["type"] == "aggregation":
        return f"Your total {metric} is ₹{data.get('value', 0)}."

    if structured["type"] == "comparison":
        return (
            f"Current: ₹{data.get('current', 0)}, "
            f"Previous: ₹{data.get('previous', 0)}, "
            f"Growth: {data.get('growth', '0%')}."
        )

    if structured["type"] == "insight":
        return (
            f"Trend: {data.get('trend', 'stable')}. "
            f"Reason: {data.get('reason', 'no major change')}."
        )

    return "Query processed."