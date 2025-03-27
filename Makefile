.PHONY: install run run-docker build clean

# Poetry commands
install:
	poetry install

run:
	poetry run python src/main.py

# Docker commands
build:
	docker-compose build

run-docker:
	docker-compose up

# Clean up
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete 