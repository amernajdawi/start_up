#!/bin/bash

# Install dependencies if needed
pip install -r requirements.txt

# Run the FastAPI application
uvicorn app:app --host 0.0.0.0 --port 8000 