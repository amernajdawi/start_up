# Regulatory Query System Backend

This backend provides an API for querying regulatory documents using AI-powered semantic search. It uses OpenAI embeddings to vectorize document chunks and FAISS for efficient similarity search.

## Setup

### Environment Variables

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
PORT=8000
```

### Installation

#### With Python (Local Development)

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn fastapi_app:app --reload
```

#### With Docker

1. Build the Docker image:
```bash
docker build -t regulatory-query-backend .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env -v $(pwd)/data:/app/data -v $(pwd)/vector_db:/app/vector_db regulatory-query-backend
```

## API Endpoints

### Health Check
- `GET /health`
  - Returns the health status of the application and whether the vector database is initialized.

### PDF Processing Status
- `GET /process-status`
  - Returns the status of PDF processing.

### Upload PDFs
- `POST /upload-pdf`
  - Uploads PDFs for processing.
  - Body: `multipart/form-data` with PDF files.

### Query Regulatory Documents
- `POST /query`
  - Queries the regulatory documents.
  - Body:
    ```json
    {
        "query": "What are the requirements for sustainability reporting?",
        "max_results": 5,
        "max_tokens": 2000
    }
    ```

### Chat Interface
- `POST /chat`
  - Compatible with the previous chat interface.
  - Body:
    ```json
    {
        "messages": [
            {
                "role": "user",
                "content": "What are the requirements for sustainability reporting?"
            }
        ]
    }
    ```

## Directory Structure

- `fastapi_app.py`: Main FastAPI application
- `pdf_processor_openai.py`: PDF processing and embedding generation
- `query_engine_openai.py`: Query engine using FAISS and OpenAI
- `requirements.txt`: Python dependencies
- `Dockerfile`: Docker configuration
- `run.sh`: Shell script to run the application

## PDF Naming Convention

The system extracts metadata from PDF filenames following this convention:
```
{hierarchy}_{date}_{document_type}_{designation}_{abbreviation}_{publisher}.pdf
```

Example:
```
1_2023-07-31_DelVO_2023/2772_ESRS_EU.pdf
```

## Development Notes

- The system uses OpenAI embeddings for document vectorization.
- FAISS is used for efficient similarity search.
- The system processes PDFs in batches to manage memory usage.
- The vector database is persisted to disk for reuse. 