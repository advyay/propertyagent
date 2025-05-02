from fastapi import FastAPI, UploadFile, Form
from agent import query_agent

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(
    message: str = Form(...),
    mongo_uri: str = Form(...),
    mongo_db: str = Form(...),
    mongo_collections: str = Form(...),
    file: UploadFile = None,
):
    response = query_agent(
        user_input=message,
        mongo_uri=mongo_uri,
        mongo_db=mongo_db,
        mongo_collections=mongo_collections,
        uploaded_file=file
    )
    return {"response": response}
