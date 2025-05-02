from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.llms.openai import OpenAI
from pymongo import MongoClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


def query_agent(
    user_input: str,
    mongo_uri: str,
    mongo_db: str,
    mongo_collections: str,
    uploaded_file: Optional[any] = None
) -> str:
    documents = []

    # --- Load from uploaded file ---
    if uploaded_file:
        try:
            file_content = uploaded_file.file.read().decode("utf-8")
            documents.append(Document(text=file_content, metadata={"source": uploaded_file.filename}))
            print(f"✅ Loaded uploaded file: {uploaded_file.filename}")
        except Exception as e:
            print(f"⚠️ Failed to read uploaded file: {e}")

    # --- Load from MongoDB ---
    try:
        collections = [col.strip() for col in mongo_collections.split(",")]
        client = MongoClient(mongo_uri)
        db = client[mongo_db]

        for collection_name in collections:
            cursor = db[collection_name].find({}, limit=100)
            for record in cursor:
                text_chunks = [f"{k}: {v}" for k, v in record.items() if k != "_id"]
                full_text = " | ".join(text_chunks)
                documents.append(Document(text=full_text, metadata={"source": collection_name}))

        client.close()
        print(f"✅ Loaded MongoDB documents from: {collections}")
    except Exception as e:
        print(f"❌ Error loading MongoDB data: {e}")

    # --- Final Check ---
    if not documents:
        return "No documents found from uploaded file or MongoDB."

    # --- LLM Setup ---
    llm = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), model="gpt-3.5-turbo")
    Settings.llm = llm

    # --- Indexing and Query ---
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    response = query_engine.query(user_input)

    return str(response)
