@echo off
echo Starting AI Chat Backend with Poetry...
cd backend

echo Installing Poetry (if not already installed)...
pip install poetry

echo Setting up the Poetry environment...
poetry install

echo Starting the FastAPI server...
poetry run uvicorn app:app --host 0.0.0.0 --port 8000 