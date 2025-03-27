import os
import asyncio
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
from typing import List, Optional
import json

from query_engine_openai import get_query_engine
from pdf_processor_openai import DATA_DIR, process_pdfs

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Regulatory Query API",
    description="API for querying regulatory documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    max_tokens: Optional[int] = 2000

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    tokens_used: Optional[int] = None

class HealthResponse(BaseModel):
    status: str
    vector_db: str
    document_count: Optional[int] = None

class MessageContent(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageContent]

# Global variables
processing_status = {"status": "idle", "progress": 0, "message": ""}

# Initialize query engine on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing query engine...")
    engine = await get_query_engine()
    if engine.documents:
        logger.info(f"Loaded {len(engine.documents)} document chunks.")
    else:
        logger.warning("No documents loaded. Check data directory or upload PDFs.")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    engine = await get_query_engine()
    return {
        "status": "healthy",
        "vector_db": "initialized" if engine.documents else "not initialized",
        "document_count": len(engine.documents) if engine.documents else 0
    }

# PDF processing status endpoint
@app.get("/process-status")
async def get_processing_status():
    return processing_status

# Upload PDF endpoint
@app.post("/upload-pdf")
async def upload_pdf(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    # Check if processing is already happening
    if processing_status["status"] == "processing":
        raise HTTPException(
            status_code=409,
            detail="PDF processing is already in progress. Please try again later."
        )
    
    try:
        # Create data directory if it doesn't exist
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
        # Save files to data directory
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is not a PDF"
                )
                
            file_path = os.path.join(DATA_DIR, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
        # Update status and start processing in background
        processing_status.update({
            "status": "processing",
            "progress": 0,
            "message": f"Starting to process {len(files)} PDF files"
        })
        
        # Process PDFs in background
        background_tasks.add_task(process_pdfs_background)
        
        return {"message": f"Uploaded {len(files)} files. Processing started in background."}
    
    except Exception as e:
        logger.error(f"Error uploading PDFs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading PDFs: {str(e)}"
        )

async def process_pdfs_background():
    """Process PDFs in background task."""
    global processing_status
    try:
        processing_status["message"] = "Processing PDFs and generating embeddings..."
        # Process PDFs
        documents = await process_pdfs()
        
        if documents:
            # Reinitialize the query engine
            engine = await get_query_engine()
            await engine.initialize()
            processing_status.update({
                "status": "completed",
                "progress": 100,
                "message": f"Successfully processed PDFs. Created {len(documents)} document chunks."
            })
        else:
            processing_status.update({
                "status": "failed",
                "progress": 0,
                "message": "Failed to process PDFs. Check logs for details."
            })
    except Exception as e:
        logger.error(f"Error in background PDF processing: {e}")
        processing_status.update({
            "status": "failed",
            "progress": 0,
            "message": f"Error: {str(e)}"
        })

# Query endpoint
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        engine = await get_query_engine()
        if not engine.initialized:
            await engine.initialize()
            
        if not engine.documents:
            raise HTTPException(
                status_code=404,
                detail="No documents found in the vector database. Please upload PDFs first."
            )
            
        result = await engine.answer_query(request.query, max_tokens=request.max_tokens)
        
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "tokens_used": result.get("tokens_used")
        }
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

# Chat endpoint (compatibility with previous API)
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Get the last user message
        user_query = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_query = msg.content
                break
        
        if not user_query:
            raise HTTPException(
                status_code=400,
                detail="No user message found in the chat history"
            )
        
        # Process the query
        engine = await get_query_engine()
        result = await engine.answer_query(user_query)
        
        # Format sources for the response
        formatted_sources = []
        for source in result.get("sources", []):
            # Extract filename from the source path
            filename = os.path.basename(source.get("source", ""))
            
            # Format document info
            doc_type = source.get("document_type", "Unknown")
            designation = source.get("designation", "Unknown")
            publisher = source.get("publisher", "Unknown")
            
            formatted_sources.append({
                "title": f"{doc_type} {designation} ({publisher})",
                "filename": filename,
                "link": f"/data/{filename}"
            })
        
        # Build the response
        response = {
            "response": result.get("answer", ""),
            "sources": formatted_sources,
            "model": "OpenAI " + os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "tokens_used": result.get("tokens_used")
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )

# Run with: uvicorn fastapi_app:app --reload
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=port, reload=True) 