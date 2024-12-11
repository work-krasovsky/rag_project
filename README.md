# RAG Project

## Technologies

- Python 3.10
- Milvus vector database
- OpenAI

## How to run locally

1. Copy `.env.example` to `.env` and fill data
2. Run `docker compose up --build -d`

## Update knowledge base query

For updating knowledge base, upload of PDF/Text file or plain text.

POST http://127.0.0.1:5000/upload

Body:
```
JSON with "text" string field 

OR 

form-data with "file" field
```

## Process query

To process user query.

POST http://127.0.0.1:5000/process

Body:

```
JSON with "text" string field
```