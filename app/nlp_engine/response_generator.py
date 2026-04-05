# app/nlp_engine/response_generator.py

def generate_response(query, structured, data):

    if structured["type"] == "aggregation":
        return f"Total {structured.get('metric')} is {data.get('value')}."

    if structured["type"] == "comparison":
        return f"Current: {data.get('current')}, Previous: {data.get('previous')}, Growth: {data.get('growth')}."

    if structured["type"] == "insight":
        return f"Trend: {data.get('trend')}, Reason: {data.get('reason')}."

    return "Could not generate response."