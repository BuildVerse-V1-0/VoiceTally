# app/nlp_engine/entity_extraction/date_parser.py

def parse_date(query: str):

    query = query.lower()

    if "last month" in query:
        return "last_month"

    if "last 2 months" in query:
        return "last_2_months"

    if "last 3 months" in query:
        return "last_3_months"

    if "quarter" in query:
        return "last_quarter"

    return None