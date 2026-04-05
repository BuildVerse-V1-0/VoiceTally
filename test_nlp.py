from app.nlp_engine.query_builder import process_query

while True:
    query = input("\nAsk: ")

    if query == "exit":
        break

    result = process_query(query)

    print("\nResponse:", result["response"])
    print("Data:", result["data"])