import os
import json
import numpy as np
import logging
import asyncio
import faiss
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pdf_processor_openai import initialize_vector_db, build_faiss_index, create_embedding, VECTOR_DIR

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

class RegulatoryQueryEngine:
    """Query engine for regulatory documents using FAISS and OpenAI."""
    
    def __init__(self):
        """Initialize the query engine."""
        self.documents = None
        self.index = None
        self.vectors = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the vector database and FAISS index."""
        if self.initialized:
            return
            
        self.documents = await initialize_vector_db()
        if not self.documents:
            logger.warning("No documents loaded in query engine.")
            return False
            
        # Build FAISS index
        self.index, self.vectors = build_faiss_index(self.documents)
        if not self.index:
            logger.warning("Failed to build FAISS index.")
            return False
            
        logger.info(f"Query engine initialized with {len(self.documents)} document chunks.")
        self.initialized = True
        return True
    
    async def search(self, query, top_k=5):
        """Search for documents most similar to the query."""
        if not self.initialized:
            await self.initialize()
            
        if not self.documents or not self.index:
            return []
        
        try:
            # Create vector representation of the query
            query_vector = await create_embedding(query)
            
            # Convert to numpy array
            query_vector_np = np.array([query_vector], dtype=np.float32)
            
            # Search using FAISS
            distances, indices = self.index.search(query_vector_np, top_k)
            
            # Create result objects
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < 0 or idx >= len(self.documents):
                    continue
                    
                doc = self.documents[idx]
                results.append({
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "distance": float(distances[0][i])
                })
            
            return results
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []
    
    async def answer_query(self, query, max_tokens=2000):
        """Answer a regulatory query based on the documents and OpenAI."""
        # Search for relevant documents
        results = await self.search(query)
        
        if not results:
            return {
                "answer": "I couldn't find any information related to your query in the regulatory documents.",
                "sources": []
            }
        
        try:
            # Extract sources (avoid duplicates)
            sources = []
            source_files = set()
            for result in results:
                source_file = result["metadata"]["source"]
                if source_file not in source_files:
                    source_files.add(source_file)
                    sources.append({
                        "source": source_file,
                        "document_type": result["metadata"].get("document_type", "Unknown"),
                        "publisher": result["metadata"].get("publisher", "Unknown"),
                        "publication_date": result["metadata"].get("publication_date", "Unknown"),
                        "designation": result["metadata"].get("designation", "Unknown"),
                        "abbreviation": result["metadata"].get("abbreviation", "Unknown"),
                        "filename": result["metadata"].get("filename", os.path.basename(source_file))
                    })
            
            # Build context from top results
            context_parts = []
            for i, result in enumerate(results):
                metadata = result["metadata"]
                source_info = f"Document {i+1} [{metadata.get('document_type', 'Unknown')} {metadata.get('designation', '')} {metadata.get('abbreviation', '')} - {metadata.get('publisher', 'Unknown')}]:"
                context_parts.append(f"{source_info}\n{result['content']}")
            
            context = "\n\n".join(context_parts)
            
            # Use OpenAI to generate an answer based on the context
            system_message = """
            You are an AI assistant specialized in regulatory compliance. 
            Answer the user's question based on the provided regulatory document excerpts.
            Be precise, accurate, and cite the specific regulations where possible.
            Format your response in a professional, clear manner.
            Include specific section references, official designations, and document types when relevant.
            If the information is not available in the provided context, acknowledge this limitation.
            Do not make up information or cite nonexistent regulations.
            """
            
            prompt = f"""
            Query: {query}
            
            Context from regulatory documents:
            {context}
            
            Answer the query based on the provided context from regulatory documents.
            """
            
            # Call OpenAI API
            response = await client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.2
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                "answer": answer,
                "sources": sources,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": f"I encountered an error while processing your query. Please try again later.",
                "sources": sources if 'sources' in locals() else []
            }

# Singleton instance
_query_engine = None

async def get_query_engine():
    """Get the singleton instance of the query engine."""
    global _query_engine
    if not _query_engine:
        _query_engine = RegulatoryQueryEngine()
        await _query_engine.initialize()
    return _query_engine

async def main():
    """Test the engine."""
    engine = await get_query_engine()
    result = await engine.answer_query("What are the requirements for sustainability reporting?")
    print(result["answer"])
    print("\nSources:")
    for source in result["sources"]:
        print(f"- {source['document_type']} ({source['publisher']})")

if __name__ == "__main__":
    asyncio.run(main()) 