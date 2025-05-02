from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from agent import query_agent

app = FastAPI()

# ✅ Enable CORS (Streamlit or web clients need this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set specific origin(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Root health check
@app.get("/")
def root():
    return {"message": "✅ FastAPI backend is running. Use POST /chat to query the AI agent."}

# ✅ Optional /ping endpoint
@app.get("/ping")
def ping():
    return {"status": "ok"}

# ✅ Main endpoint
@app.post("/chat")
async def chat_endpoint(
    message: str = Form(...),
    mongo_uri: str = Form(...),
    mongo_db: str = Form(...),
    mongo_collections: str = Form(...),
    file: UploadFile = None,
):
    try:
        response = query_agent(
            user_input=message,
            mongo_uri=mongo_uri,
            mongo_db=mongo_db,
            mongo_collections=mongo_collections,
            uploaded_file=file,
        )
        return {"response": response}
    except Exception as e:
        return {"response": f"❌ Internal Server Error: {str(e)}"}

