import os
import re
import chromadb
from sentence_transformers import SentenceTransformer
from config import URL, DB_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL
from scraper import scrape


model = SentenceTransformer(EMBEDDING_MODEL)


def clean_text(text):
    # replace markdown image tags with line breaks to preserve separation
    text = re.sub(r'!\[.*?\]\(.*?\)', '\n', text)
    # remove markdown links but keep the link text
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # remove WordPress API/REST junk, JSON blocks, CSS, script content
    text = re.sub(r'\{[^}]{200,}\}', '', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'/wp-json/\S+', '', text)
    text = re.sub(r'https?://\S+', '', text)
    # remove repeated nav/menu items (lines that are just "* text")
    lines = text.split('\n')
    seen_lines = set()
    deduped = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('* ') and stripped in seen_lines:
            continue
        seen_lines.add(stripped)
        deduped.append(line)
    text = '\n'.join(deduped)
    # collapse whitespace but keep single newlines as separators
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    # add separator between names/roles that run together
    # (handles "Dr. South\nArlene\nDental Hygienist" staying distinct)
    text = re.sub(r'\n', ' | ', text)
    return text.strip()


def chunk_text(text):
    text = clean_text(text)
    words = text.split()
    chunks = []
    for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = " ".join(words[i:i + CHUNK_SIZE])
        if chunk:
            chunks.append(chunk)
    return chunks


def collection_name_from_url(url):
    name = url.replace("https://", "").replace("http://", "")
    name = "".join(c if c.isalnum() else "_" for c in name)
    name = name.strip("_")
    return name[:63]


def save_to_db(chunks, collection_name):
    client = chromadb.PersistentClient(path=DB_DIR)
    # delete old collection if it exists, so we start fresh
    try:
        client.delete_collection(name=collection_name)
    except ValueError:
        pass
    collection = client.create_collection(name=collection_name)

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    embeddings = model.encode(chunks).tolist()

    collection.add(ids=ids, embeddings=embeddings, documents=chunks)
    print(f"Saved {len(chunks)} chunks to '{collection_name}'")


if __name__ == "__main__":
    print("Scraping...")
    text = scrape(URL)
    print(f"Got {len(text)} characters")

    print("Chunking...")
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks")

    print("Embedding and saving...")
    name = collection_name_from_url(URL)
    save_to_db(chunks, name)
    print("Done!")
