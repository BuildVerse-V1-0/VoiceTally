from app.nlp_engine.query_builder import process_query

# 🔥 MEMORY CONTEXT
context = {
    "last_metric": None,
    "last_time": None,
    "last_intent": None
}


def main():
    print("\n🚀 VoiceTally AI Assistant")
    print("Ask anything about your business data (type 'exit' to quit)\n")

    while True:
        user_input = input("🧠 You: ")

        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        result = process_query(user_input, context)

        print("\n🤖 VoiceTally:")
        print(result.get("response", "No response"))

        # 🔥 UPDATE MEMORY
        if result.get("structured"):
            structured = result["structured"]
            context["last_metric"] = structured.get("metric")
            context["last_time"] = structured.get("time")
            context["last_intent"] = structured.get("type")

        print("\n" + "-"*50)


if __name__ == "__main__":
    main()