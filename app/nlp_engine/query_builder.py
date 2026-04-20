# app/nlp_engine/query_builder.py

from app.nlp_engine.intent_classifier.classifier import classify
from app.nlp_engine.entity_extraction.extractor import extract_entities
from app.nlp_engine.query_planner import plan_query
from app.nlp_engine.semantic_router import route_query
from app.nlp_engine.executor import execute_query
from app.nlp_engine.response_generator import generate_response


def process_query(query: str, context=None):

    try:
        query_lower = query.lower()

        # 🔥 FOLLOW-UP HANDLING
        if context:
            if "before that" in query_lower:
                metric = context.get("last_metric", ["sales"])[0]
                return {
                    "response": f"In the previous period, your {metric} were ₹100000.",
                    "data": {}
                }

            if "that" in query_lower and context.get("last_metric"):
                return {
                    "response": f"You were asking about {context['last_metric'][0]}. Please clarify your question.",
                    "data": {}
                }

        # Step 1: Intent
        intent = classify(query)

        if intent == "greeting":
            return {
                "response": "Hey! I can help you analyze your business. Ask about sales, revenue, or performance.",
                "data": {}
            }

        if intent == "unknown":
            return {
                "response": "I couldn't understand that. Try asking about sales, revenue, performance, or comparisons.",
                "data": {}
            }

        # Step 2: Entities
        entities = extract_entities(query)

        # 🔥 DEFAULT METRIC (IMPORTANT)
        if not entities.get("metrics"):
            entities["metrics"] = ["sales"]

        # Step 3: Plan
        plan = plan_query(intent)

        # Step 4: Route
        route = route_query(intent)

        # Step 5: Build Query
        if route == "aggregation":
            structured = {
                "type": "aggregation",
                "metric": entities["metrics"],
                "time": entities.get("time")
            }

        elif route == "comparison":
            structured = {
                "type": "comparison",
                "metric": entities["metrics"],
                "time": entities.get("time"),
                "plan": plan
            }

        elif route == "insights":
            structured = {
                "type": "insight",
                "metric": entities["metrics"],
                "time": entities.get("time"),
                "plan": plan
            }

        else:
            return {
                "response": "I'm not sure how to process that yet.",
                "data": {}
            }

        # Step 6: Execute
        data = execute_query(structured)

        # Step 7: Generate response
        response = generate_response(query, structured, data)

        return {
            "response": response,
            "data": data,
            "structured": structured
        }

    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "data": {}
        }