import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY environment variable not found")
    api_key = "dummy_key_for_testing"  # For development only

# Initialize client without problematic parameters
client = AsyncOpenAI(api_key=api_key)
LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Create FastAPI app
app = FastAPI(
    title="AI Chat API",
    description="Simple API for connecting the frontend to OpenAI",
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
class MessageContent(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageContent]
    temperature: float = 0.7

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": LLM_MODEL
    }

# Chat endpoint - Match the exact path that frontend expects
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Log incoming request
        logger.info(f"Received chat request with {len(request.messages)} messages")
        
        # Format messages for OpenAI
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Call OpenAI API
        logger.info(f"Calling OpenAI API with model: {LLM_MODEL}")
        try:
            response = await client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=request.temperature
            )
            
            # Return the response
            result = {
                "response": response.choices[0].message.content,
                "model": LLM_MODEL,
                "tokens_used": response.usage.total_tokens
            }
            logger.info(f"Successfully generated response with {result['tokens_used']} tokens")
            return result
            
        except Exception as openai_error:
            logger.error(f"OpenAI API error: {openai_error}")
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI API error: {str(openai_error)}"
            )
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )

# Also add a root endpoint to handle redirected requests
@app.post("/chat")
async def chat_redirect(request: ChatRequest):
    # This handles the case where nginx might strip the /api prefix
    return await chat(request)

# Run with: uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True) 