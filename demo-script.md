# Demo Script

## Setup

Open a terminal in the project directory with the virtual environment activated.

---

**"Here's how our LLM chatbot works. We scrape a website, turn its content into searchable vectors, and then chat with it -- all running locally, no cloud APIs."**

## Step 1: Configure

Open `config.py` and show the URL, priority pages, and max pages settings.

**"First, we point it at the website we want to chat with. We set the URL, pick specific pages we want to make sure get scraped -- like the contact page or the team page -- and set a max page limit. That's it for config."**

## Step 2: Scrape and Index

```powershell
$env:PYTHONUTF8=1; python embedder.py
```

**"The `$env:PYTHONUTF8=1` part just tells Python to use UTF-8 encoding. Windows defaults to an older encoding that crashes on special characters. This is a Windows-only thing -- Linux and Mac don't need it."**

**"Now we run the indexing tool. This does two things: it scrapes the website pages, then converts the text into embeddings -- numerical vectors that capture the meaning of the words. Because they're in vector space, we can compare the semantic relationships between words. 'Contact info' and 'phone number' are close together even though they share no words. That's what makes this smarter than keyword search."**

Wait for it to finish. Point out the number of pages scraped and chunks saved.

## Step 3: Chat

```powershell
$env:PYTHONUTF8=1; python chat.py
```

Ask: **"What is the contact info for the real estate agent?"**

**"When we ask a question, the system embeds our query into the same vector space, finds the chunks with the most similar meaning, and appends them into the prompt that gets sent to the LLM. The model reads those chunks and generates an answer grounded in the actual website content. It's not guessing -- it's reading."**

Ask one or two more questions to show range:
- "What services do they offer?"
- "Who is on the team?"

## Closing

**"The key thing here: the LLM never memorized the website. We just hand it the relevant excerpts right before it answers. That means we can point this at any website, re-index in minutes, and the chatbot is ready to go."**
