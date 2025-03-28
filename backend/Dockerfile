FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy Poetry configuration
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not use virtualenvs inside Docker
RUN poetry config virtualenvs.create false

# Install dependencies (without dev dependencies and without trying to install the current project)
RUN poetry install --without dev --no-root

# Copy the application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 