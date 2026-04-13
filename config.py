# config.py
# All project settings in one place. No CLI args, no env files -- just edit this.

import os

# Target website to scrape and chat with
URL = "https://northyorkfamilydentistry.com/"

# Subpages to scrape first, before crawling discovered links.
# These are guaranteed to be scraped (within MAX_PAGES).
# Set to [] if no specific pages are needed.
PRIORITY_PAGES = [
    "https://northyorkfamilydentistry.com/contact-us/",
    "https://northyorkfamilydentistry.com/why-nyfd/our-team/",
]
# Maximum number of pages to scrape from the site
MAX_PAGES = 15

# Local directory where the ChromaDB vector database is stored
DB_DIR = "./dbs"

# Ollama model used for generating chat responses
MODEL = "llama3.2"
# Directory where Ollama stores downloaded model files
OLLAMA_MODELS_DIR = "E:/AI tools/llm_models"

# Sentence-transformers model used to embed text chunks into vectors
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# Number of words per chunk when splitting scraped text
CHUNK_SIZE = 500
# Number of overlapping words between adjacent chunks (prevents lost context at boundaries)
CHUNK_OVERLAP = 50
# Number of most-relevant chunks retrieved per query
TOP_K = 5

os.environ["OLLAMA_MODELS"] = OLLAMA_MODELS_DIR
