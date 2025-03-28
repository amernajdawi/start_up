# Backend for AI Chat Assistant

This is a lightweight backend that provides a direct connection between the frontend and OpenAI's API.

## Features

- Simple FastAPI app that forwards requests to OpenAI
- Poetry for dependency management
- Docker support for easy deployment
- Async API for improved performance

## Setup

### Using Poetry (Recommended)

```bash
# Install Poetry (if needed)
pip install poetry

# Install dependencies
poetry install

# Run the server
poetry run uvicorn app:app --reload
```

### Environment Variables

Create a `.env` file in the root directory with:

```
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /api/chat` - Chat endpoint that forwards messages to OpenAI

## Docker

The backend can be built and run as a Docker container:

```bash
docker build -t ai-chat-backend .
docker run -p 8000:8000 --env-file ../.env ai-chat-backend
```

Or preferably, use Docker Compose from the project root:

```bash
docker-compose up --build
``` 