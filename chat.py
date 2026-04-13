from config import URL
from embedder import collection_name_from_url
from retriever import retrieve
from llm import ask


def main():
    collection_name = collection_name_from_url(URL)
    print(f"Chatting with: {URL}")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit"):
            print("Bye!")
            break

        chunks = retrieve(question, collection_name)
        print("Bot: ", end="")
        ask(question, chunks)
        print()


if __name__ == "__main__":
    main()
