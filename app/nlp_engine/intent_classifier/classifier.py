# app/nlp_engine/intent_classifier/classifier.py

from .rule_based import classify as rule_based_classify

import openai


def llm_parse_intent(query: str):
    try:
        prompt = f"""
        Convert this business query into structured JSON.

        Query: "{query}"

        Output:
        {{
          "intent": "...",
          "metrics": [],
          "dimensions": [],
          "time_range": "",
          "comparison": "",
          "aggregation": ""
        }}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return eval(response['choices'][0]['message']['content'])

    except Exception as e:
        print("LLM failed:", e)
        return None


def classify(query: str):

    # Step 1: Rule-based
    result = rule_based_classify(query)

    # Step 2: LLM fallback
    if result == "unknown" or not result:
        llm_result = llm_parse_intent(query)
        if llm_result:
            return llm_result

    return result