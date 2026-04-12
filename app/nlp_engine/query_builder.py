# app/nlp_engine/query_builder.py

from app.nlp_engine.intent_classifier.classifier import classify
from app.nlp_engine.entity_extraction.extractor import extract_entities
from app.nlp_engine.query_planner import plan_query
from app.nlp_engine.semantic_router import route_query
from app.nlp_engine.executor import execute_query
from app.nlp_engine.response_generator import generate_response


def build_aggregation_query(intent_data, entities):
    return {
        "type": "aggregation",
        "metric": entities.get("metrics", ["sales"]),
        "time": entities.get("time")
    }


def build_comparison_query(intent_data, entities, plan):
    return {
        "type": "comparison",
        "metric": entities.get("metrics", ["sales"]),
        "time": entities.get("time"),
        "plan": plan
    }


def build_insight_query(intent_data, entities, plan):
    return {
        "type": "insight",
        "metric": entities.get("metrics", ["sales"]),
        "time": entities.get("time"),
        "plan": plan
    }


def process_query(query: str):

    try:
        intent = classify(query)
        entities = extract_entities(query)

        plan = plan_query(intent)
        route = route_query(intent)

        if route == "aggregation":
            structured = build_aggregation_query(intent, entities)

        elif route == "comparison":
            structured = build_comparison_query(intent, entities, plan)

        elif route == "insights":
            structured = build_insight_query(intent, entities, plan)

        else:
            return {
                "response": "Could not understand query.",
                "data": {}
            }

        data = execute_query(structured)
        response = generate_response(query, structured, data)

        return {
            "response": response if response else "No response generated",
            "data": data if data else {},
            "structured": structured
        }

    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "data": {}
        }