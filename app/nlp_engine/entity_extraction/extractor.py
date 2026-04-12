# app/nlp_engine/entity_extraction/extractor.py

from .business_entities import extract_business_entities
from .date_parser import parse_date


def extract_entities(query):

    entities = {
        "metrics": [],
        "filters": {},
        "time": None
    }

    try:
        data = extract_business_entities(query)
        if data:
            entities.update(data)
    except:
        pass

    try:
        date_data = parse_date(query)
        if date_data:
            entities["time"] = date_data
    except:
        pass

    return entities