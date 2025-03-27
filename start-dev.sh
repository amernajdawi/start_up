#!/bin/bash

echo "Starting development environment..."

# Make script executable (in case it isn't already)
chmod +x backend/run.sh

# Start backend and frontend-dev services
docker-compose up backend frontend-dev 