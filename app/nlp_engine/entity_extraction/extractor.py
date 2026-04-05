# nlp_engine/entity_extraction/extractor.py

from .business_entities import extract_business_entities
from .date_parser import parse_date

import openai


# -------------------------------
# RULE-BASED EXTRACTION
# -------------------------------
def rule_based_extract(query):

    entities = {
        "metrics": [],
        "filters": {},
        "time": None
    }

    # Extract business entities
    try:
        business_data = extract_business_entities(query)
        if business_data:
            entities.update(business_data)
    except Exception as e:
        print("Business entity extraction failed:", e)

    # Extract date/time
    try:
        date_data = parse_date(query)
        if date_data:
            entities["time"] = date_data
    except Exception as e:
        print("Date parsing failed:", e)

    return entities


# -------------------------------
# LLM FALLBACK FOR METRICS
# -------------------------------
def llm_extract_metrics(query):

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"Extract key business metrics from this query: {query}"
                }
            ]
        )

        content = response['choices'][0]['message']['content']
        return [content]

    except Exception as e:
        print("LLM metric extraction failed:", e)
        return []


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def extract_entities(query):

    entities = rule_based_extract(query)

    # If metrics missing → use LLM
    if not entities.get("metrics"):
        entities["metrics"] = llm_extract_metrics(query)

    return entities