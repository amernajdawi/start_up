FROM python:3.9-slim

# Install essential tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install pip and basic packages
RUN pip install --upgrade pip setuptools wheel 