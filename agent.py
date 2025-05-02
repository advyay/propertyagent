from llama_index.core import VectorStoreIndex, Settings, Document, StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
from pymongo import MongoClient
from typing import Optional
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

def compute_mongo_fingerprint(client, db_name, collections):
    import json
    fingerprint_data = []

    for col_name in collections:
        records = list(client[db_name][col_name].find({}, {'_id': 0}))
        fingerprint_data.append({col_name: records})

    json_str = json.dumps(fingerprint_data, sort_keys=True)
    return hashlib.md5(json_str.encode()).hexdigest()


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
            cursor = db[collection_name].find({})  # Reduce load
            for record in cursor:
                text_chunks = [f"{k}: {v}" for k, v in record.items() if k != "_id"]
                full_text = " | ".join(text_chunks)
                documents.append(Document(text=full_text, metadata={"source": collection_name}))

        client.close()
        print(f"✅ Loaded MongoDB documents from: {collections}")
    except Exception as e:
        print(f"❌ Error loading MongoDB data: {e}")

    if not documents:
        return "No documents found from uploaded file or MongoDB."

    # --- Setup OpenAI LLM ---
    llm = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), model="gpt-3.5-turbo")
    Settings.llm = llm

    # --- Setup Persistent Indexing ---
    client = MongoClient(mongo_uri)
    fingerprint = compute_mongo_fingerprint(client, mongo_db, collections)
    index_dir = f"./storage/index_{fingerprint}"


    if os.path.exists(index_dir):
        print("✅ Loading cached index...")
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        index = load_index_from_storage(storage_context)
    else:
        print("📦 Building index for new session...")
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=index_dir)

    # --- Smart Query Handling ---
    query_engine = index.as_query_engine(
        system_prompt="""
You are a data analyst AI agent.

- When asked about 'best performing agents', 'top revenue', or 'highest attendance', you should compare values and provide a ranked answer if possible.
- If data is ambiguous or inconsistent, clearly explain that.
- Use numeric aggregation when total commissions, counts, or metrics are involved.
"""
    )
    response = query_engine.query(user_input)
    return str(response)
