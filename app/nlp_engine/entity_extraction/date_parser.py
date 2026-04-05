# app/nlp_engine/entity_extraction/date_parser.py

def parse_date(query: str):
    query = query.lower()

    if "last year" in query:
        return "last_year"

    if "last month" in query:
        return "last_month"

    if "last 3 months" in query:
        return "last_3_months"

    if "march" in query:
        return "march"

    return None