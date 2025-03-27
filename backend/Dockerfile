FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
# Create a default empty .env file
RUN echo "# Default .env file - override with volume mount" > .env

# Expose Flask port
EXPOSE 5000

# Run Flask
CMD ["python", "backend/app.py"] 