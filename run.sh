#!/bin/bash

# Function to stop background processes when the script exits
function cleanup {
    echo "Stopping all processes..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Set up trap to call cleanup when script exits
trap cleanup EXIT INT TERM

echo "Starting AI Chat Application (Frontend + Backend)"
echo "------------------------------------------------"

# Start backend
echo "Starting backend server..."
./backend/run.sh &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait a moment for backend to initialize
sleep 2

# Start frontend
echo "Starting frontend server..."
./frontend/run.sh &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo "------------------------------------------------"
echo "Frontend running at: http://localhost:8501"
echo "Backend API running at: http://localhost:5000"
echo "Press Ctrl+C to stop all services"
echo "------------------------------------------------"

# Keep the script running
wait 