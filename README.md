# AI Chat Assistant

A simple chat application that connects a React frontend directly to OpenAI's API through a lightweight FastAPI backend.

## Features

- **Direct OpenAI Integration**: Connect directly to OpenAI's language models
- **Simple React Frontend**: Clean, responsive chat interface with dark/light modes
- **Lightweight FastAPI Backend**: Minimal backend that forwards requests to OpenAI
- **Easy Deployment**: Docker support for simple deployment
- **Poetry Package Management**: Uses Poetry for reliable dependency management

## Getting Started

### Prerequisites

- Docker and Docker Compose for containerized deployment
- Python 3.10+ for local backend development (with Poetry)
- Node.js and npm for local frontend development

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Set up environment variables:
   Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   OPENAI_MODEL=gpt-4o-mini
   ```

## Running the Application

### Using Docker (Recommended)

The easiest way to run the application is using Docker:

```bash
./run-docker.bat  # On Windows
# OR
docker-compose up --build  # On any platform
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Local Development

#### Backend (with Poetry)

```bash
cd backend
poetry install
poetry run uvicorn app:app --reload
```

#### Frontend (with npm)

```bash
cd frontend
npm install
npm start
```

## Project Structure

```
├── backend/
│   ├── app.py                # FastAPI application
│   ├── pyproject.toml        # Poetry configuration
│   ├── Dockerfile            # Backend Docker configuration
│   └── run-poetry.bat        # Script to run backend with Poetry
├── frontend/
│   ├── src/                  # React application source
│   ├── public/               # Static assets
│   └── package.json          # Node.js dependencies
├── docker-compose.yml        # Docker Compose configuration
├── nginx.conf                # Nginx configuration for serving frontend
└── .env                      # Environment variables
```

## API Endpoints

- `POST /api/chat`: Send messages to OpenAI and get responses
- `GET /health`: Health check endpoint

## License

[License information]
