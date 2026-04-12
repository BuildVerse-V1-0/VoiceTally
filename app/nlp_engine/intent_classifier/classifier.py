# app/nlp_engine/intent_classifier/classifier.py

from .rule_based import classify as rule_based_classify


def classify(query: str):
    return rule_based_classify(query)