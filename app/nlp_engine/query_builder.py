# nlp_engine/query_builder.py

from app.nlp_engine.intent_classifier.classifier import classify
from app.nlp_engine.entity_extraction.extractor import extract_entities
from app.nlp_engine.query_planner import plan_query
from app.nlp_engine.semantic_router import route_query
from app.nlp_engine.executor import execute_query
from app.nlp_engine.response_generator import generate_response

import openai


# ----------------------------------------
# FALLBACK (LLM RESPONSE IF EVERYTHING FAILS)
# ----------------------------------------
def fallback_response(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a business analyst."},
                {"role": "user", "content": query}
            ]
        )

        return response['choices'][0]['message']['content']

    except Exception as e:
        return f"Fallback failed: {str(e)}"


# ----------------------------------------
# BUILD AGGREGATION QUERY
# ----------------------------------------
def build_aggregation_query(intent_data, entities):

    return {
        "type": "aggregation",
        "metric": entities.get("metrics", []),
        "filters": entities.get("filters", {}),
        "time_range": entities.get("time"),
        "aggregation": (
            intent_data.get("aggregation")
            if isinstance(intent_data, dict)
            else intent_data
        )
    }


# ----------------------------------------
# BUILD COMPARISON QUERY
# ----------------------------------------
def build_comparison_query(intent_data, entities, plan):

    return {
        "type": "comparison",
        "metric": entities.get("metrics", []),
        "time_range": entities.get("time"),
        "comparison": (
            intent_data.get("comparison")
            if isinstance(intent_data, dict)
            else "previous_period"
        ),
        "plan": plan
    }


# ----------------------------------------
# BUILD INSIGHT QUERY (WHY / ANALYSIS)
# ----------------------------------------
def build_insight_query(intent_data, entities, plan):

    return {
        "type": "insight",
        "metric": entities.get("metrics", []),
        "time_range": entities.get("time"),
        "analysis_steps": plan
    }


# ----------------------------------------
# MAIN FUNCTION (ENTRY POINT)
# ----------------------------------------
def process_query(query: str):

    try:
        # ----------------------------------------
        # STEP 1: INTENT CLASSIFICATION
        # ----------------------------------------
        intent_data = classify(query)

        # ----------------------------------------
        # STEP 2: ENTITY EXTRACTION
        # ----------------------------------------
        entities = extract_entities(query)

        # ----------------------------------------
        # STEP 3: QUERY PLANNING
        # ----------------------------------------
        plan = plan_query(intent_data)

        # ----------------------------------------
        # STEP 4: ROUTING
        # ----------------------------------------
        route = route_query(intent_data)

        # ----------------------------------------
        # STEP 5: BUILD STRUCTURED QUERY
        # ----------------------------------------
        if route == "aggregation":
            structured_query = build_aggregation_query(intent_data, entities)

        elif route == "comparison":
            structured_query = build_comparison_query(intent_data, entities, plan)

        elif route == "insights":
            structured_query = build_insight_query(intent_data, entities, plan)

        else:
            return {
                "query": query,
                "response": fallback_response(query)
            }

        # ----------------------------------------
        # STEP 6: EXECUTE QUERY (DATA LAYER)
        # ----------------------------------------
        data_result = execute_query(structured_query)

        # ----------------------------------------
        # STEP 7: GENERATE FINAL HUMAN RESPONSE
        # ----------------------------------------
        final_response = generate_response(
            query,
            structured_query,
            data_result
        )

        # ----------------------------------------
        # FINAL OUTPUT
        # ----------------------------------------
        return {
            "query": query,
            "intent": intent_data,
            "entities": entities,
            "plan": plan,
            "structured_query": structured_query,
            "data": data_result,
            "response": final_response
        }

    except Exception as e:
        return {
            "error": str(e),
            "query": query
        }