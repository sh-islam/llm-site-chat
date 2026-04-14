# LLM Site Chat

A local Retrieval-Augmented Generation (RAG) pipeline that enables natural language interaction with any website. The system scrapes a target URL, indexes its content into a vector database, and serves answers through a locally hosted LLM. All processing occurs on-device -- no cloud APIs, no external data transmission.

## Demo

https://github.com/user-attachments/assets/bd89515d-358b-4705-9de5-e158f86179db

## Overview

1. A target website URL is provided via configuration
2. The scraper crawls the site and extracts text content across multiple pages
3. Extracted text is split into overlapping chunks and embedded into vectors
4. Vectors are stored in a persistent local database
5. At query time, the most relevant chunks are retrieved via similarity search
6. Retrieved chunks are injected into the LLM prompt as context
7. The LLM generates a response grounded in the retrieved content

The model does not retain or learn from the website data. It receives relevant excerpts at inference time and reasons over them -- functionally equivalent to an open-book examination.

## Setup

### Prerequisites

- Python 3.10+
- NVIDIA GPU (6GB+ VRAM recommended)
- [Ollama](https://ollama.com) installed and running

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd website-llm-chat

# Create and activate a virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the headless browser for the scraper (required once)
playwright install chromium

# Pull the LLM model
ollama pull llama3.2
```

### Configuration

All settings are centralized in `config.py`:

```python
URL = "https://example.com/"                   # target website
PRIORITY_PAGES = [                             # subpages to scrape first (guaranteed)
    "https://example.com/about/",
    "https://example.com/contact/",
]
MAX_PAGES = 15                                 # maximum pages to scrape
DB_DIR = "./dbs"                               # vector database storage path
MODEL = "llama3.2"                             # Ollama model name
OLLAMA_MODELS_DIR = "E:/AI tools/llm_models"   # Ollama model storage path
EMBEDDING_MODEL = "all-MiniLM-L6-v2"           # sentence-transformers model
CHUNK_SIZE = 500                               # words per chunk
CHUNK_OVERLAP = 50                             # word overlap between chunks
TOP_K = 5                                      # chunks retrieved per query
```

## Usage

### Step 1: Scrape and index (run once per site)

```bash
python embedder.py
```

This scrapes the target website, chunks the extracted text, generates embeddings, and persists them to the local vector database. Re-running is only necessary when the source website content changes.

### Step 2: Start the chat interface

```bash
python chat.py
```

Enter natural language queries to receive answers grounded in the scraped website content. Type `quit` or `exit` to terminate the session.

### Windows PowerShell Note

If encoding errors occur, set the UTF-8 environment variable before execution:

```powershell
$env:PYTHONUTF8=1; python embedder.py
$env:PYTHONUTF8=1; python chat.py
```

## Project Structure

```
website-llm-chat/
├── config.py        # centralized configuration
├── scraper.py       # website crawler, returns clean text
├── embedder.py      # text chunking, embedding, and database storage
├── retriever.py     # vector similarity search against ChromaDB
├── llm.py           # prompt construction and Ollama streaming
├── chat.py          # main interactive loop
├── requirements.txt
└── dbs/             # vector database (auto-generated)
```

## Documentation

### What is RAG?

RAG (Retrieval-Augmented Generation) is a technique for supplementing a language model with external knowledge at inference time, without modifying the model's weights.

The three components:

- **Retrieval** -- a vector similarity search identifies text passages relevant to the input query
- **Augmentation** -- the retrieved passages are concatenated into the model's prompt, providing domain-specific context the model was not trained on
- **Generation** -- the model produces a response conditioned on both the query and the injected context

The model does not memorize or internalize the source material. The relevant text is inserted into the prompt as a string before each inference call. The model reads it and reasons over it the same way it processes any other input text.

### Why RAG over fine-tuning?

Fine-tuning modifies the model's internal weights by training on a domain-specific dataset. RAG leaves the model untouched and supplies knowledge externally.

|                     | RAG                    | Fine-Tuning                  |
|---------------------|------------------------|------------------------------|
| Setup time          | Minutes                | Hours to days                |
| GPU requirements    | Inference only         | High-end GPU for training    |
| Stale data          | Re-scrape and re-index | Retrain the entire model     |
| Labeled data needed | No                     | Yes                          |
| Cost                | Free (local)           | Significant                  |

Fine-tuning alters model *behavior* (tone, style, task specialization). RAG provides model *knowledge* (domain-specific facts). For the use case of querying website content, RAG is the appropriate approach.

### Embeddings

An embedding is a fixed-length numerical vector representing the semantic meaning of a text passage. Passages with similar meaning produce vectors that are geometrically close in the embedding space.

During indexing, each chunk from the website is converted into a vector. At query time, the input question is also embedded, and the system retrieves the chunks whose vectors have the highest cosine similarity to the query vector. This is a semantic similarity search, not keyword matching -- it captures meaning rather than exact word overlap.

This project uses `all-MiniLM-L6-v2` from the sentence-transformers library. It is a pretrained model (~80MB) that runs locally without an API key. The semantic relationships between words and phrases (e.g., "apple" and "fruit" producing similar vectors) are learned during pretraining -- the model was trained on large text corpora and already understands which concepts are related. ChromaDB does not compute or understand these relationships; it only stores the vectors and performs numerical distance comparisons at query time.

### Chunking

Language models have a finite context window -- an entire website cannot be passed as a single input. The text is therefore divided into overlapping segments (default: 500 words per chunk, 50-word overlap between adjacent chunks).

The overlap ensures continuity at chunk boundaries. Without it, sentences that span the boundary between two chunks would be split and lose coherence during retrieval.

### Technology Choices

#### Ollama (LLM runtime)

Ollama abstracts model loading, quantization, and GPU memory allocation. The alternative -- manually loading models via the transformers library or llama.cpp -- requires significantly more boilerplate for model lifecycle management. Ollama reduces this to a single pull command and a single API call.

#### ChromaDB (vector database)

|             | ChromaDB                             | FAISS                                 |
|-------------|--------------------------------------|---------------------------------------|
| Persistence | Automatic, saves to disk             | Manual, requires explicit save/load   |
| Metadata    | Built-in (URLs, chunk IDs, etc.)     | None, requires external management    |
| Setup       | `pip install chromadb`               | Similar, but more integration code    |
| Best for    | Small-to-medium scale applications   | High-throughput production systems    |

FAISS (developed by Meta) offers superior performance at large scale and is widely used in production systems. However, it provides only a raw index -- persistence, metadata management, and filtering must be implemented separately. ChromaDB encapsulates all of these into a simple API.

For production deployment at small-to-medium scale -- such as a single company website served by 5-10 concurrent chatbot instances -- ChromaDB is well-suited. In this scenario, the database is written once during indexing and subsequently only read by the chatbot instances. The data changes infrequently, only requiring re-indexing when the source website is updated. ChromaDB handles tens of thousands of chunks and concurrent read access without issue.

Migration to FAISS or a managed vector database (Pinecone, Weaviate) would only become necessary at significantly larger scale: millions of documents, hundreds of simultaneously indexed sources, or thousands of concurrent users.

#### crawl4ai (web scraper)

crawl4ai renders JavaScript-heavy pages via a headless browser and returns clean markdown. The primary alternative, BeautifulSoup, only parses static HTML and cannot handle dynamically rendered content without supplementary tools like Selenium. crawl4ai combines both capabilities in a single package.

#### sentence-transformers (embeddings)

Runs entirely on-device with no API key required. The `all-MiniLM-L6-v2` model is lightweight (~80MB) and produces high-quality embeddings for English text. Cloud-based alternatives such as OpenAI's embedding API require authentication and transmit data externally.

### Prompt Construction

When a query is submitted, the system constructs a prompt by concatenating a system instruction, the retrieved context chunks, and the user's question:

```
System: A helpful assistant that answers questions about a website.
Only use the provided context. If the context does not contain the
answer, state that there is insufficient information.

Context:
[retrieved chunk 1]
---
[retrieved chunk 2]
---
[retrieved chunk 3]

User: What services are offered?
```

The model receives this as a single input and generates a response grounded in the provided context. This is the "augmentation" step -- the prompt is augmented with retrieved content. The mechanism is string concatenation; no special model modification is involved.

## Dependencies

| Package               | Purpose                                          |
|-----------------------|--------------------------------------------------|
| `crawl4ai`            | Web scraping with JavaScript rendering support   |
| `sentence-transformers`| Local text embedding generation                 |
| `chromadb`            | Persistent vector database for chunk storage     |
| `ollama`              | Python client for the Ollama LLM runtime         |
