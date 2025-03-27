#!/bin/bash
echo "Starting backend Flask API..."

# Ensure dependencies are installed
poetry install

# Run the Flask app 
poetry run python backend/app.py 