import ollama
from config import MODEL


def ask(question, chunks):
    context = "\n\n---\n\n".join(chunks)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that answers questions about a website. "
                "Use ONLY the following context to answer. If the context doesn't contain "
                "the answer, say you don't have enough information.\n\n"
                f"Context:\n{context}"
            ),
        },
        {"role": "user", "content": question},
    ]

    stream = ollama.chat(model=MODEL, messages=messages, stream=True)

    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)

    print()


if __name__ == "__main__":
    test_chunks = ["This is a test website about Python programming."]
    ask("What is this website about?", test_chunks)
