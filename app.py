# app.py

# from fastapi import FastAPI
# from pydantic import BaseModel
# from langchain_community.document_loaders import DirectoryLoader
# from langchain_ollama import OllamaEmbeddings, OllamaLLM
# from langchain_community.vectorstores import Chroma
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory
# from fastapi.responses import JSONResponse
# import os
# import time
# import logging

# # Logging setup
# logging.basicConfig(level=logging.INFO)

# app = FastAPI(title="DSCPL – Spiritual AI Companion API")

# # ========= Vector Store and Model Initialization =========
# PERSIST_DIR = "./data/chroma_db"

# if os.path.exists(PERSIST_DIR):
#     logging.info("Loading existing vectorstore...")
#     embedding = OllamaEmbeddings(model="llama3")
#     vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding)
# else:
#     logging.info("Creating vectorstore from documents...")
#     loader = DirectoryLoader("content/", glob="**/*.txt")
#     docs = loader.load()
#     embedding = OllamaEmbeddings(model="llama3")
#     vectordb = Chroma.from_documents(docs, embedding=embedding, persist_directory=PERSIST_DIR)
#     vectordb.persist()

# # Initialize LLM and conversational chain
# llm = OllamaLLM(model="llama3")
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# rag_chain = ConversationalRetrievalChain.from_llm(
#     llm=llm,
#     retriever=vectordb.as_retriever(),
#     memory=memory,
# )

# # ========= Request Body Model =========
# class Query(BaseModel):
#     category: str
#     topic: str
#     start_program: bool = False
#     program_length: int = 7
#     chat_history: list = []  # list of dicts: [{"role": "user", "content": "..."}]

# # ========= Prompt Formatter =========
# def format_prompt(category, topic, start_program=False, program_length=7):
#     base_intro = "You are DSCPL, a spiritual AI assistant and companion. The user selected:"
#     overview = (f"\nBegin a {program_length}-day spiritual journey for '{topic}' in '{category}'. "
#                 "Provide a weekly summary and daily encouragement. Confirm the start, prompt for user goals, "
#                 "and instruct how notifications/calendar sync will work.") if start_program else ""

#     if category == "Devotion":
#         return f"""{base_intro} Devotion topic: '{topic}'{overview}

# Reply with:
# 1. 5-minute Bible Reading for '{topic}'
# 2. Short Prayer
# 3. Faith Declaration
# 4. Recommended Video (suggest video topic if unable to show actual video)
# """
#     elif category == "Prayer":
#         return f"""{base_intro} Prayer topic: '{topic}'{overview}

# Use ACTS format:
# - Adoration
# - Confession
# - Thanksgiving
# - Supplication
# Include daily prayer prompt.
# """
#     elif category == "Meditation":
#         return f"""{base_intro} Meditation topic: '{topic}'{overview}

# Respond with:
# - Relevant scripture focus
# - Meditation prompts (What does this reveal? How can I live this today?)
# - Breathing guide (Inhale 4s → Hold 4s → Exhale 4s)
# """
#     elif category == "Accountability":
#         return f"""{base_intro} Accountability Area: '{topic}'{overview}

# Offer:
# - Related scripture
# - Truth declarations
# - Alternative action suggestions
# - SOS feature guidance (encouragement, action plan)
# """
#     else:  # Just Chat
#         return f"""{base_intro} General Chat ('{topic}'){overview}
# Respond warmly and conversationally, ask if user wants support for any spiritual goal.
# """

# # ========= API Endpoint =========
# @app.post("/chat/")
# async def chat_endpoint(query: Query):
#     prompt = format_prompt(query.category, query.topic, query.start_program, query.program_length)
#     chat_input = f"{prompt}\nUser: {query.topic}"

#     try:
#         start_time = time.time()
#         output = rag_chain.invoke({"question": chat_input, "chat_history": query.chat_history})
#         elapsed = time.time() - start_time
#         logging.info(f"Processed '{query.category} - {query.topic}' in {elapsed:.2f} seconds")
#         return {"answer": output["answer"]}

#     except Exception as e:
#         logging.error(f"Error during chain execution: {e}")
#         return JSONResponse(status_code=500, content={"answer": f"Server error: {str(e)}"})

# # ========= Health Check Endpoint =========
# @app.get("/")
# async def root():
#     return {"status": "DSCPL API is running"}







# import time
# import logging
# import os
# from fastapi import FastAPI
# from pydantic import BaseModel
# from langchain_community.document_loaders import DirectoryLoader
# from langchain_ollama import OllamaEmbeddings, OllamaLLM
# from langchain_community.vectorstores import Chroma
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory

# logging.basicConfig(level=logging.INFO)
# app = FastAPI()

# PERSIST_DIR = "./data/chroma_db"
# CONTENT_DIR = "content/"
# EMBED_MODEL = "llama3:8b"  # smaller + faster
# LLM_MODEL = "llama3:8b"    # smaller + faster

# # ✅ 1. Initialize once at startup
# logging.info("🔄 Initializing Embeddings...")
# embedding = OllamaEmbeddings(model=EMBED_MODEL)

# if os.path.exists(PERSIST_DIR):
#     logging.info("📂 Loading existing Chroma DB...")
#     vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding)
# else:
#     logging.info("📄 Creating Chroma DB from local documents...")
#     loader = DirectoryLoader(CONTENT_DIR, glob="**/*.txt")
#     docs = loader.load()
#     vectordb = Chroma.from_documents(docs, embedding=embedding, persist_directory=PERSIST_DIR)
#     vectordb.persist()

# # ✅ 2. Load LLM once
# logging.info("🧠 Loading LLM model...")
# llm = OllamaLLM(model=LLM_MODEL)

# # ✅ 3. Warm-up call to avoid first-request delay
# try:
#     logging.info("🔥 Warming up model...")
#     _ = llm.invoke("Hello, just warming up.")
# except Exception as e:
#     logging.error(f"Warm-up failed: {e}")

# # ✅ 4. Pre-create chain
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# rag_chain = ConversationalRetrievalChain.from_llm(
#     llm=llm,
#     retriever=vectordb.as_retriever(search_kwargs={"k": 3}),  # less retrieval = faster
#     memory=memory,
# )

# class Query(BaseModel):
#     category: str
#     topic: str
#     start_program: bool = False
#     program_length: int = 7
#     chat_history: list = []

# def format_prompt(category, topic, start_program=False, program_length=7):
#     base_intro = "You are DSCPL, a spiritual AI assistant and companion."
#     overview = (
#         f"\nBegin a {program_length}-day spiritual journey for '{topic}' in '{category}'. "
#         "Provide a weekly summary and daily encouragement."
#     ) if start_program else ""

#     if category == "Devotion":
#         return f"""{base_intro} Devotion topic: '{topic}'{overview}

# Reply with:
# 1. 5-minute Bible Reading for '{topic}'
# 2. Short Prayer
# 3. Faith Declaration
# 4. Recommended Video (suggest topic if no actual video available)
# """
#     elif category == "Prayer":
#         return f"""{base_intro} Prayer topic: '{topic}'{overview}

# Use ACTS format:
# - Adoration
# - Confession
# - Thanksgiving
# - Supplication
# Include daily prayer prompt.
# """
#     elif category == "Meditation":
#         return f"""{base_intro} Meditation topic: '{topic}'{overview}

# Respond with:
# - Relevant scripture
# - Meditation prompts
# - Breathing guide (Inhale 4s → Hold 4s → Exhale 4s)
# """
#     elif category == "Accountability":
#         return f"""{base_intro} Accountability Area: '{topic}'{overview}

# Offer:
# - Related scripture
# - Truth declarations
# - Alternative action suggestions
# - SOS feature guidance
# """
#     else:
#         return f"{base_intro} General Chat ('{topic}'){overview}"

# @app.post("/chat/")
# async def chat_endpoint(query: Query):
#     prompt = format_prompt(query.category, query.topic, query.start_program, query.program_length)
#     chat_input = f"{prompt}\nUser: {query.topic}"

#     start_time = time.time()
#     try:
#         output = rag_chain({"question": chat_input, "chat_history": query.chat_history})
#         logging.info(f"✅ Response generated in {time.time() - start_time:.2f} seconds")
#         return {"answer": output["answer"]}
#     except Exception as e:
#         logging.error(f"❌ Error: {e}")
#         return {"answer": "Sorry, an error occurred. Please try again."}










import os
import re
import time
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
app = FastAPI()

# Allow local Streamlit origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONTENT_DIR = "content"
MAX_BULLETS = 10  # limit number of bullets returned


class Query(BaseModel):
    category: str  # Devotion, Prayer, Meditation, Accountability, Just Chat etc.
    topic: str
    start_program: bool = False
    program_length: int = 7
    chat_history: list = []


def normalize(s: str):
    """Lower, strip non-alnum (but keep spaces) for comparison."""
    return re.sub(r"[^a-z0-9 ]", "", s.lower().strip())


def find_matching_file(category: str, topic: str):
    """
    Attempts to find a file in content/<category> that matches the topic.
    Returns path or None.
    Matching strategy order:
    1. Filename startswith(topic normalized)
    2. Filename contains topic
    3. Search inside files for a heading or first line that matches topic
    """
    cat_folder = os.path.join(CONTENT_DIR, category.lower())
    if not os.path.isdir(cat_folder):
        return None

    topic_norm = normalize(topic).replace(" ", "")
    # list all candidate files
    candidates = []
    for fname in os.listdir(cat_folder):
        if not fname.lower().endswith((".md", ".txt")):
            continue
        candidates.append(os.path.join(cat_folder, fname))

    # 1 & 2: filename matching
    for p in candidates:
        base = os.path.splitext(os.path.basename(p))[0]
        base_norm = normalize(base).replace(" ", "")
        if base_norm == topic_norm or base_norm.startswith(topic_norm) or topic_norm in base_norm:
            return p

    # 3: search inside files for a heading matching topic
    for p in candidates:
        try:
            with open(p, "r", encoding="utf-8") as f:
                text = f.read(2048)  # read start portion
            # check headings like "# Peace" or first line
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            if not lines:
                continue
            # check first few lines for topic presence
            for line in lines[:6]:
                if topic.lower() in line.lower():
                    return p
        except Exception:
            continue

    return None


def markdown_to_bullets(text: str):
    """
    Turn a markdown/text document into short bullet points.
    Strategy:
    - Remove excessive markup
    - Split into lines, keep lines that look like sentences or list items
    - Collapse long paragraphs into 1-2 bullets each
    - Return up to MAX_BULLETS bullets
    """
    # Remove code blocks and images
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    # Replace headings with newlines
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    # Convert common list markers to plain lines
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    # Remove markdown links but keep text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Normalize whitespace
    text = re.sub(r"\n{2,}", "\n\n", text).strip()

    bullets = []
    # Use paragraphs first (split by double newline)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for p in paragraphs:
        # turn paragraph into one or two short sentences (split by sentence end)
        sentences = re.split(r"(?<=[.!?])\s+", p)
        # drop extremely short fragments
        clean_sents = [s.strip() for s in sentences if len(s.strip()) > 20]
        if not clean_sents:
            # fallback: use the paragraph trimmed
            clean_sents = [p.strip()[:200]]
        for s in clean_sents[:2]:  # up to 2 bullets per paragraph
            line = re.sub(r"\s+", " ", s).strip()
            bullets.append(line)
            if len(bullets) >= MAX_BULLETS:
                break
        if len(bullets) >= MAX_BULLETS:
            break

    # As a fallback, if we got no bullets, split by lines
    if not bullets:
        for ln in text.splitlines():
            ln = ln.strip()
            if ln and len(ln) > 20:
                bullets.append(ln)
                if len(bullets) >= MAX_BULLETS:
                    break

    # prepend bullet marker
    bullets = [f"• {b}" for b in bullets[:MAX_BULLETS]]
    return "\n".join(bullets)


@app.post("/chat/")
async def chat_endpoint(query: Query):
    start = time.time()
    category = query.category or ""
    topic = query.topic or ""

    # Basic safety: require topic
    if not topic.strip():
        return {"answer": "Please provide a topic."}

    # Try to find local content first
    file_path = find_matching_file(category, topic)
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = f.read()
            bullets = markdown_to_bullets(raw)
            elapsed = time.time() - start
            logging.info(f"Served local file {file_path} in {elapsed:.3f}s")
            # Return a short header + bullets
            header = f"**{category} — {topic}**\n\n"
            return {"answer": header + bullets}
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return {"answer": "Sorry — couldn't read the local content. Try again or ask to generate content."}

    # No local content — we avoid heavy LLM calls automatically
    logging.info(f"No local file found for {category}/{topic}. ({time.time()-start:.3f}s)")
    return {"answer": f"Sorry, I don't have prewritten content for **{topic}** in **{category}**. Would you like me to generate a short summary instead?"}
