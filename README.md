# LlamaIndex AI Agent

## Features
- Accepts PDF, DOCX, TXT files (place in `/data`)
- Indexes documents and allows natural language queries
- Uses OpenAI or custom LLM

## Setup

1. Install requirements:
```
pip install -r requirements.txt
```

2. Add your OpenAI API key:
```
cp .env.example .env
```

3. Start the server:
```
uvicorn main:app --reload
```

4. Query via POST:
```
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message": "What is the refund policy?"}'
```
