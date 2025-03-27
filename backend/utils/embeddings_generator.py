import os
from typing import List, Dict, Any
import numpy as np
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmbeddingsGenerator:
    """
    A utility class for generating text embeddings using OpenAI models.
    """
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        """
        Initialize the embeddings generator with specified parameters.
        
        Args:
            api_key (str, optional): OpenAI API key (defaults to environment variable)
            model (str): Embedding model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided or not found in environment variables")
        
        # Initialize the embeddings model
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.api_key,
            model=self.model
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding vector for a single text.
        
        Args:
            text (str): Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        if not text:
            return []
        
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return []
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for a batch of texts.
        
        Args:
            texts (List[str]): List of texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            # Filter out empty strings to avoid API errors
            valid_texts = [text for text in texts if text]
            embeddings = self.embeddings.embed_documents(valid_texts)
            
            # Return embeddings in the same order as input texts (empty for empty inputs)
            result = []
            valid_idx = 0
            
            for text in texts:
                if text:
                    result.append(embeddings[valid_idx])
                    valid_idx += 1
                else:
                    result.append([])
            
            return result
        except Exception as e:
            print(f"Error generating batch embeddings: {str(e)}")
            return [[] for _ in texts]
    
    def process_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a list of text chunks and add embeddings to each chunk.
        
        Args:
            chunks (List[Dict[str, Any]]): List of chunks to process
            
        Returns:
            List[Dict[str, Any]]: Chunks with embeddings added
        """
        if not chunks:
            return []
        
        # Extract chunk content for batch embedding
        texts = [chunk.get("content", "") for chunk in chunks]
        
        # Generate embeddings for all texts
        embeddings = self.generate_batch_embeddings(texts)
        
        # Add embeddings to chunks
        result = []
        for i, chunk in enumerate(chunks):
            chunk_with_embedding = chunk.copy()
            chunk_with_embedding["embedding"] = embeddings[i]
            result.append(chunk_with_embedding)
        
        return result 