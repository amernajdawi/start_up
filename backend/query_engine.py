import os
import json
import numpy as np
from pdf_processor import simple_vector_representation, initialize_vector_db, VECTOR_DIR

class RegulatoryQueryEngine:
    """Query engine for regulatory documents."""
    
    def __init__(self):
        """Initialize the query engine."""
        self.documents = None
        self.initialize()
    
    def initialize(self):
        """Initialize the vector database."""
        self.documents = initialize_vector_db()
        if not self.documents:
            print("Warning: No documents loaded in query engine.")
    
    def vector_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors."""
        # Convert to numpy arrays if they aren't already
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        # Calculate dot product
        dot_product = np.dot(v1, v2)
        
        # Calculate magnitudes
        mag1 = np.linalg.norm(v1)
        mag2 = np.linalg.norm(v2)
        
        # Avoid division by zero
        if mag1 == 0 or mag2 == 0:
            return 0
        
        # Calculate cosine similarity
        return dot_product / (mag1 * mag2)
    
    def search(self, query, top_k=5):
        """Search for documents most similar to the query."""
        if not self.documents:
            return []
        
        # Create vector representation of the query
        query_vector = simple_vector_representation(query)
        query_vector_np = np.array(query_vector)
        
        # Convert document vectors to numpy array for faster computation
        doc_vectors = []
        for doc in self.documents:
            doc_vectors.append(doc["vector"])
        
        # Convert to numpy array
        doc_vectors_np = np.array(doc_vectors)
        
        # Calculate dot products in one batch operation
        dot_products = np.dot(doc_vectors_np, query_vector_np)
        
        # Calculate magnitudes
        query_magnitude = np.linalg.norm(query_vector_np)
        doc_magnitudes = np.linalg.norm(doc_vectors_np, axis=1)
        
        # Calculate cosine similarities
        similarities = dot_products / (doc_magnitudes * query_magnitude)
        
        # Get indices of top results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Create result objects
        results = []
        for idx in top_indices:
            doc = self.documents[idx]
            results.append({
                "content": doc["content"],
                "metadata": doc["metadata"],
                "similarity": float(similarities[idx])
            })
        
        return results
    
    def answer_query(self, query):
        """Answer a regulatory query based on the documents."""
        # Search for relevant documents
        results = self.search(query)
        
        if not results:
            return {
                "answer": "I couldn't find any information related to your query in the regulatory documents.",
                "sources": []
            }
        
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
                    "abbreviation": result["metadata"].get("abbreviation", "Unknown")
                })
        
        # Build context from top results
        context = "\n\n".join([f"Document {i+1}:\n{r['content']}" for i, r in enumerate(results)])
        
        # Create answer based on context
        # In a full implementation, you would use an LLM here
        # For this version, we'll use a simplified approach
        doc_types = ", ".join(set(s["document_type"] for s in sources if s["document_type"] != "Unknown"))
        publishers = ", ".join(set(s["publisher"] for s in sources if s["publisher"] != "Unknown"))
        
        answer = f"Based on the {doc_types} documents from {publishers}, I found information related to your query. "
        
        # Add something about the top result
        if results:
            top_doc = results[0]
            if "abbreviation" in top_doc["metadata"] and top_doc["metadata"]["abbreviation"] != "Unknown":
                answer += f"The {top_doc['metadata']['abbreviation']} "
                if "designation" in top_doc["metadata"] and top_doc["metadata"]["designation"] != "Unknown":
                    answer += f"({top_doc['metadata']['designation']}) "
                answer += "mentions: "
            
            # Add a snippet from the top result
            content = top_doc["content"]
            if len(content) > 300:
                sentences = content.split('. ')
                snippet = '. '.join(sentences[:3]) + '.'
            else:
                snippet = content
            
            answer += snippet
        
        return {
            "answer": answer,
            "sources": sources
        }

# Singleton instance
_query_engine = None

def get_query_engine():
    """Get the singleton instance of the query engine."""
    global _query_engine
    if not _query_engine:
        _query_engine = RegulatoryQueryEngine()
    return _query_engine

if __name__ == "__main__":
    # Test the engine
    engine = get_query_engine()
    result = engine.answer_query("What are the requirements for sustainability reporting?")
    print(result["answer"])
    print("\nSources:")
    for source in result["sources"]:
        print(f"- {source['document_type']} ({source['publisher']})") 