from app.nlp_engine.query_builder import process_query


def main():
    print("\n🚀 VoiceTally AI Assistant")
    print("Ask anything about your business data (type 'exit' to quit)\n")

    while True:
        user_input = input("🧠 You: ")

        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        result = process_query(user_input)

        print("\n🤖 VoiceTally:")
        print(result.get("response", "No response generated."))
        print("\n" + "-"*50)


if __name__ == "__main__":
    main()