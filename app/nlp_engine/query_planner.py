# nlp_engine/query_planner.py

def plan_query(intent_data):
    plan = []

    if isinstance(intent_data, dict):

        if intent_data.get("comparison"):
            plan = [
                "fetch_current_period",
                "fetch_previous_period",
                "compare_results"
            ]

        elif intent_data.get("intent") == "diagnostic":
            plan = [
                "fetch_data",
                "analyze_trends",
                "detect_anomalies",
                "find_causes"
            ]

        else:
            plan = ["simple_query"]

    else:
        plan = ["simple_query"]

    return plan