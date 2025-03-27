import os
import glob
import re
import json
import asyncio
from PyPDF2 import PdfReader
import numpy as np
from tqdm import tqdm
import gc
import openai
from openai import AsyncOpenAI
import faiss
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Define the directories
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
VECTOR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vector_db")

# Ensure the vector database directory exists
if not os.path.exists(VECTOR_DIR):
    os.makedirs(VECTOR_DIR)

def extract_document_info(filename):
    """Extract metadata from the filename based on the schema:
    e.g., 1_2023-07-31_DelVO_2023/2772_ESRS_EU.pdf
    """
    basename = os.path.basename(filename)
    basename = os.path.splitext(basename)[0]  # Remove extension
    
    # Try to match the pattern
    pattern = r"(\d+)_(\d{4}-\d{2}-\d{2})_([A-Za-z]+)_(\d+/\d+|\d+)_([A-Za-z]+)_([A-Za-z]+)"
    match = re.match(pattern, basename)
    
    if match:
        hierarchy, pub_date, doc_type, designation, abbr, publisher = match.groups()
        return {
            "hierarchy": hierarchy,
            "publication_date": pub_date,
            "document_type": doc_type,
            "designation": designation,
            "abbreviation": abbr,
            "publisher": publisher,
            "filename": basename + ".pdf"
        }
    
    # Try alternative pattern
    alt_pattern = r"(\d+)_([^_]+)_(\d{4}-\d{2}-\d{2})_([A-Za-z]+)_([^_]+)_([A-Za-z&]+)"
    match = re.match(alt_pattern, basename)
    
    if match:
        hierarchy, section, pub_date, doc_type, abbr, publisher = match.groups()
        return {
            "hierarchy": hierarchy,
            "section": section,
            "publication_date": pub_date,
            "document_type": doc_type,
            "abbreviation": abbr,
            "publisher": publisher,
            "filename": basename + ".pdf"
        }
    
    # If the pattern doesn't match, use a more relaxed approach
    parts = basename.split('_')
    if len(parts) >= 4:
        result = {
            "hierarchy": parts[0] if parts[0].isdigit() else "1",
            "filename": basename + ".pdf"
        }
        
        # Try to extract date if it matches the format
        date_pattern = r"\d{4}-\d{2}-\d{2}"
        for part in parts:
            if re.match(date_pattern, part):
                result["publication_date"] = part
                break
        
        # Use other parts as they appear
        for i, part in enumerate(parts):
            if i >= 2 and part.isalpha():
                if "document_type" not in result:
                    result["document_type"] = part
                elif "abbreviation" not in result:
                    result["abbreviation"] = part
                elif "publisher" not in result:
                    result["publisher"] = part
        
        return result
    
    # If nothing else works, return minimal metadata
    return {
        "filename": basename + ".pdf",
        "document_type": "Unknown",
        "publisher": "Unknown"
    }

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        # Process one page at a time to minimize memory usage
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            # Clear references to reduce memory usage
            page = None
            
            # Every 10 pages, chunk and process text to avoid memory buildup
            if i > 0 and i % 10 == 0:
                # Release memory for processed pages
                gc.collect()
                
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return ""

def create_chunks(text, chunk_size=500, overlap=100):
    """Split text into overlapping chunks of specified size."""
    if not text:
        return []
    
    if len(text) < chunk_size:
        return [text]
        
    chunks = []
    start = 0
    text_length = len(text)
    
    # Process text in segments to avoid memory pressure
    while start < text_length:
        # Calculate end with consideration for text length
        end = min(start + chunk_size, text_length)
        
        # Try to find a good breaking point (period, paragraph, space)
        if end < text_length:
            # Look for natural breaks
            break_found = False
            for break_char in ['\n\n', '.', '\n', ';', ',', ' ']:
                # Look for the break character within a window
                window_start = max(end - 30, start)
                pos = text.rfind(break_char, window_start, end)
                if pos != -1 and pos > start:
                    end = pos + 1
                    break_found = True
                    break
            
            # If no good break point found, just use the calculated end
            if not break_found:
                end = min(end, text_length)
        
        # Add the chunk
        chunks.append(text[start:end])
        
        # Move start position for next chunk, with overlap
        start = end - overlap
        
        # Avoid small final chunk
        if text_length - start < chunk_size / 3:
            if start < text_length:
                chunks.append(text[start:text_length])
            break
    
    return chunks

async def create_embedding(text):
    """Create embedding for text using OpenAI API."""
    try:
        response = await client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error creating embedding: {e}")
        # Fallback to simple vector representation if API fails
        return simple_vector_representation(text)

def simple_vector_representation(text):
    """Create a simple vector representation of text.
    This is a fallback when OpenAI's API is unavailable.
    """
    # Handle empty text
    if not text or len(text) == 0:
        return [0.0] * 36  # 26 letters + 10 digits
    
    # Process text in smaller chunks to reduce memory usage for very large texts
    sample_size = min(len(text), 5000)  # Limit sample size for very large texts
    if len(text) > sample_size:
        # Sample from beginning, middle and end
        begin = text[:sample_size//3]
        middle_start = len(text)//2 - sample_size//6
        middle = text[middle_start:middle_start + sample_size//3]
        end = text[-sample_size//3:]
        sample_text = begin + middle + end
    else:
        sample_text = text
    
    # Calculate character frequencies
    char_count = {}
    total_chars = 0
    
    # Only count alphanumeric characters
    for char in sample_text.lower():
        if char.isalnum():
            char_count[char] = char_count.get(char, 0) + 1
            total_chars += 1
    
    # Avoid division by zero
    if total_chars == 0:
        return [0.0] * 36
    
    # Create fixed-size vector (26 letters + 10 digits)
    vector = []
    for c in 'abcdefghijklmnopqrstuvwxyz0123456789':
        vector.append(char_count.get(c, 0) / total_chars)
    
    return vector

async def process_pdf_batch(batch_files, temp_vector_file):
    """Process a batch of PDF files."""
    batch_documents = []
    
    # Process each PDF in this small batch
    for pdf_file in tqdm(batch_files, desc=f"Processing batch"):
        try:
            # Extract text
            text = extract_text_from_pdf(pdf_file)
            if not text:
                continue
            
            # Extract metadata
            metadata = extract_document_info(pdf_file)
            
            # Use smaller chunk size for very large files
            file_size = os.path.getsize(pdf_file) / (1024 * 1024)  # Size in MB
            chunk_size = 250 if file_size > 5 else 500  # Smaller chunks for larger files
            overlap = 50 if file_size > 5 else 100
            
            # Split text into chunks
            chunks = create_chunks(text, chunk_size, overlap)
            logger.info(f"Created {len(chunks)} chunks from {pdf_file}")
            
            # Process all chunks asynchronously
            embedding_tasks = [create_embedding(chunk) for chunk in chunks]
            embeddings = await asyncio.gather(*embedding_tasks)
            
            # Create document objects
            for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                doc = {
                    "content": chunk,
                    "vector": vector,
                    "metadata": {
                        **metadata,
                        "chunk_id": i,
                        "source": pdf_file
                    }
                }
                batch_documents.append(doc)
            
            # Free up memory
            del text
            del chunks
            gc.collect()
            
        except MemoryError:
            logger.error(f"Memory error processing {pdf_file}, skipping...")
            continue
        except Exception as e:
            logger.error(f"Error processing {pdf_file}: {e}")
    
    # Save this batch to the temporary file
    if batch_documents:
        # Read existing data
        try:
            with open(temp_vector_file, 'r') as f:
                existing_docs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_docs = []
        
        # Append new documents
        existing_docs.extend(batch_documents)
        
        # Write back to file
        with open(temp_vector_file, 'w') as f:
            json.dump(existing_docs, f)
    
    return len(batch_documents)

async def process_pdfs():
    """Process all PDFs in the data directory and create a vector database."""
    # Get list of PDFs
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {DATA_DIR}")
        return None
    
    # Create vector database directory
    if not os.path.exists(VECTOR_DIR):
        os.makedirs(VECTOR_DIR)
    
    # Create a temporary file to store documents incrementally
    temp_vector_file = os.path.join(VECTOR_DIR, "vectors_temp.json")
    vector_meta_file = os.path.join(VECTOR_DIR, "vectors_meta.json")
    
    try:
        # Initialize with empty array
        with open(temp_vector_file, 'w') as f:
            f.write("[]")
        
        # Track total document chunks
        total_chunks = 0
        logger.info(f"Processing {len(pdf_files)} PDF files...")
        
        # Process files in smaller batches to reduce memory pressure
        batch_size = 2
        for batch_idx in range(0, len(pdf_files), batch_size):
            batch_files = pdf_files[batch_idx:batch_idx + batch_size]
            batch_count = await process_pdf_batch(batch_files, temp_vector_file)
            total_chunks += batch_count
            
            # Log progress
            logger.info(f"Processed batch {batch_idx//batch_size + 1}/{(len(pdf_files)+batch_size-1)//batch_size} - {batch_count} chunks created")
        
        # Rename temp file to final vector file
        vector_file = os.path.join(VECTOR_DIR, "vectors.json")
        if os.path.exists(vector_file):
            os.remove(vector_file)
        os.rename(temp_vector_file, vector_file)
        
        logger.info(f"Created {total_chunks} document chunks from {len(pdf_files)} PDF files.")
        
        # Save metadata about the vectors
        metadata = {
            "total_chunks": total_chunks,
            "pdf_count": len(pdf_files),
            "embedding_model": EMBEDDING_MODEL,
            "vector_dimension": 1536 if EMBEDDING_MODEL == "text-embedding-3-small" else 36
        }
        
        with open(vector_meta_file, 'w') as f:
            json.dump(metadata, f)
        
        # Load the final vector database
        with open(vector_file, 'r') as f:
            documents = json.load(f)
        
        return documents
        
    except Exception as e:
        logger.error(f"Error in process_pdfs: {e}")
        if os.path.exists(temp_vector_file):
            try:
                os.remove(temp_vector_file)
            except:
                pass
        return None

async def initialize_vector_db():
    """Initialize or load the vector database."""
    vector_file = os.path.join(VECTOR_DIR, "vectors.json")
    
    # If vector file exists, load it
    if os.path.exists(vector_file):
        try:
            with open(vector_file, 'r') as f:
                documents = json.load(f)
            logger.info(f"Loaded {len(documents)} document chunks from vector database.")
            return documents
        except Exception as e:
            logger.error(f"Error loading vector database: {e}")
    
    # Otherwise, process PDFs and create it
    return await process_pdfs()

def build_faiss_index(documents):
    """Build a FAISS index from document vectors."""
    if not documents:
        return None, None
    
    # Get dimension from first vector
    dimension = len(documents[0]["vector"])
    
    # Create a FAISS index
    index = faiss.IndexFlatL2(dimension)
    
    # Add vectors to the index
    vectors = np.array([doc["vector"] for doc in documents], dtype=np.float32)
    index.add(vectors)
    
    return index, vectors

async def main():
    """Main function for testing."""
    documents = await initialize_vector_db()
    if documents:
        logger.info(f"Successfully processed {len(documents)} document chunks.")
        index, vectors = build_faiss_index(documents)
        if index:
            logger.info(f"Successfully built FAISS index with {index.ntotal} vectors of dimension {index.d}.")

if __name__ == "__main__":
    asyncio.run(main()) 