# app/nlp_engine/entity_extraction/business_entities.py

def extract_business_entities(query):

    query = query.lower()

    entities = {
        "metrics": [],
        "filters": {}
    }

    # 🔥 METRIC DETECTION
    if "sales" in query:
        entities["metrics"].append("sales")

    if "revenue" in query:
        entities["metrics"].append("revenue")

    if "profit" in query:
        entities["metrics"].append("profit")

    # 🔥 PERFORMANCE → MAP TO SALES (SMART DEFAULT)
    if "performance" in query and not entities["metrics"]:
        entities["metrics"].append("sales")

    return entities