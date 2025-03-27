import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import json
from tqdm import tqdm
import numpy as np

class VectorStore:
    """
    A service class for storing and retrieving embeddings using ChromaDB.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector store with specified parameters.
        
        Args:
            persist_directory (str): Directory to persist the vector database
        """
        self.persist_directory = persist_directory
        
        # Create the directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize the ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Collection name for regulatory documents
        self.collection_name = "regulatory_documents"
        
        # Get or create the collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
            print(f"Using existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Regulatory document chunks with embeddings"}
            )
            print(f"Created new collection: {self.collection_name}")
    
    def add_chunks(self, chunks_with_embeddings: List[Dict[str, Any]]) -> None:
        """
        Add document chunks with embeddings to the vector store.
        
        Args:
            chunks_with_embeddings (List[Dict[str, Any]]): Chunks with embeddings to add
        """
        if not chunks_with_embeddings:
            return
        
        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for chunk in chunks_with_embeddings:
            # Ensure the chunk has required fields
            if not chunk.get("content") or not chunk.get("embedding"):
                continue
            
            # Create a unique ID for the chunk
            doc_id = chunk.get("metadata", {}).get("filename", "unknown")
            chunk_id = chunk.get("metadata", {}).get("chunk_id", 0)
            unique_id = f"{doc_id}_{chunk_id}"
            
            # Prepare metadata (ensuring JSON serializable)
            metadata = {}
            for key, value in chunk.get("metadata", {}).items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    metadata[key] = value
                else:
                    # Convert non-serializable values to strings
                    metadata[key] = str(value)
            
            ids.append(unique_id)
            embeddings.append(chunk["embedding"])
            documents.append(chunk["content"])
            metadatas.append(metadata)
        
        # Add data to ChromaDB in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end_idx = min(i + batch_size, len(ids))
            
            self.collection.add(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
        
        print(f"Added {len(ids)} chunks to the vector store")
    
    def similarity_search(
        self,
        query_text: str,
        query_embedding: List[float],
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in the vector store.
        
        Args:
            query_text (str): Query text (for logging only)
            query_embedding (List[float]): Query embedding vector
            n_results (int): Number of results to return
            filter_metadata (Dict[str, Any], optional): Metadata filters
            
        Returns:
            List[Dict[str, Any]]: List of similar documents
        """
        # Convert filter metadata to ChromaDB format if provided
        where = None
        if filter_metadata:
            where = {}
            for key, value in filter_metadata.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    where[key] = value
        
        # Perform the query
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        # Format the results
        formatted_results = []
        
        if results and "documents" in results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                result = {
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if "metadatas" in results else {},
                    "id": results["ids"][0][i] if "ids" in results else f"result_{i}",
                    "distance": results["distances"][0][i] if "distances" in results else None
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current collection.
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            return {
                "error": str(e),
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            } 