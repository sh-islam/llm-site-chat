import chromadb
from sentence_transformers import SentenceTransformer
from config import DB_DIR, TOP_K, EMBEDDING_MODEL


model = SentenceTransformer(EMBEDDING_MODEL)


def retrieve(question, collection_name):
    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_collection(name=collection_name)

    query_embedding = model.encode([question]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=TOP_K)

    return results["documents"][0]


if __name__ == "__main__":
    from config import URL
    from embedder import collection_name_from_url

    name = collection_name_from_url(URL)
    question = "What is this website about?"
    chunks = retrieve(question, name)

    print(f"Top {len(chunks)} chunks for: '{question}'\n")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i + 1} ---")
        print(chunk[:300])
        print()
