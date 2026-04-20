# app/nlp_engine/response_generator.py

def generate_response(query, structured, data):

    metric = structured.get("metric", ["sales"])[0]
    time = structured.get("time", "")

    time_text = ""
    if time:
        time_text = f" for {time.replace('_', ' ')}"

    if structured["type"] == "aggregation":
        return f"Your total {metric}{time_text} is ₹{data.get('value', 0)}."

    if structured["type"] == "comparison":
        return (
            f"Your {metric}{time_text} is ₹{data.get('current')}, "
            f"previously ₹{data.get('previous')}, showing {data.get('growth')} growth."
        )

    if structured["type"] == "insight":
        return f"Your {metric} shows a {data.get('trend')} due to {data.get('reason')}."

    return "Done."