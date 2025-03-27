#!/usr/bin/env python3
"""
Initialize Vector Database

This script processes PDF files in the data directory and creates a vector database for similarity search.
It extracts text from PDFs, chunks it, generates embeddings, and stores them in the vector database.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from pdf_processor_openai import process_pdfs, build_faiss_index
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vector_db_init.log')
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Initialize the vector database."""
    start_time = time.time()
    
    # Load environment variables
    load_dotenv()
    
    logger.info("Starting PDF processing and vector database initialization...")
    
    # Process PDFs
    documents = await process_pdfs()
    
    if not documents:
        logger.error("Failed to process PDFs. No documents available.")
        return
    
    logger.info(f"Successfully processed {len(documents)} document chunks.")
    
    # Build FAISS index
    index, vectors = build_faiss_index(documents)
    if index:
        logger.info(f"Successfully built FAISS index with {index.ntotal} vectors of dimension {index.d}.")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Vector database initialization completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main()) 