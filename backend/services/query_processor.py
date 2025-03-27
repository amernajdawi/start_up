import os
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv

from backend.utils.embeddings_generator import EmbeddingsGenerator

# Load environment variables
load_dotenv()

class QueryProcessor:
    """
    A service class for processing regulatory queries, finding relevant documents,
    and generating qualified answers.
    """
    
    def __init__(
        self,
        vector_store,
        embedding_generator: Optional[EmbeddingsGenerator] = None,
        api_key: str = None,
        model: str = None
    ):
        """
        Initialize the query processor with specified components.
        
        Args:
            vector_store: Vector store for retrieving relevant documents
            embedding_generator (EmbeddingsGenerator, optional): For generating query embeddings
            api_key (str, optional): OpenAI API key (defaults to environment variable)
            model (str, optional): OpenAI model for answering (defaults to environment variable)
        """
        self.vector_store = vector_store
        
        # Initialize embedding generator if not provided
        if embedding_generator:
            self.embedding_generator = embedding_generator
        else:
            self.embedding_generator = EmbeddingsGenerator(api_key=api_key)
        
        # Get API key and model from environment variables if not provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided or not found in environment variables")
        
        # Configure OpenAI API
        openai.api_key = self.api_key
    
    def process_query(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a regulatory query and generate a qualified answer.
        
        Args:
            query (str): The user's query about regulations
            n_results (int): Number of relevant documents to retrieve
            filter_metadata (Dict[str, Any], optional): Metadata filters for search
            
        Returns:
            Dict[str, Any]: Processing results including answer and sources
        """
        # Generate embedding for the query
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        if not query_embedding:
            return {
                "answer": "Sorry, I couldn't process your query. Please try again.",
                "sources": [],
                "query": query,
                "error": "Failed to generate query embedding"
            }
        
        # Search for relevant documents
        search_results = self.vector_store.similarity_search(
            query_text=query,
            query_embedding=query_embedding,
            n_results=n_results,
            filter_metadata=filter_metadata
        )
        
        if not search_results:
            return {
                "answer": "I couldn't find any relevant regulatory information for your query.",
                "sources": [],
                "query": query
            }
        
        # Generate context from search results
        context = self._generate_context(search_results)
        
        # Generate answer
        answer = self._generate_answer(query, context, search_results)
        
        # Extract and format sources
        sources = self._extract_sources(search_results)
        
        return {
            "answer": answer,
            "sources": sources,
            "query": query,
            "context_used": len(search_results)
        }
    
    def _generate_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Generate a context string from search results for the OpenAI query.
        
        Args:
            search_results (List[Dict[str, Any]]): Search results to include in context
            
        Returns:
            str: Formatted context string
        """
        context_parts = []
        
        for i, result in enumerate(search_results):
            # Extract information from the result
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            
            # Create a source reference
            source = f"Source {i+1}: "
            if "filename" in metadata:
                source += metadata["filename"]
            if "section_header" in metadata:
                source += f" - {metadata['section_header']}"
            
            # Add to context parts
            context_parts.append(f"{source}\n{content}\n")
        
        return "\n\n".join(context_parts)
    
    def _generate_answer(
        self,
        query: str,
        context: str,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate an answer to the query using OpenAI and the retrieved context.
        
        Args:
            query (str): The user's query
            context (str): Context information from search results
            search_results (List[Dict[str, Any]]): The raw search results
            
        Returns:
            str: Generated answer
        """
        try:
            # Prepare the system message with instructions
            system_message = """
You are an AI assistant specializing in regulatory information. Your task is to provide specific, 
qualified answers to questions about regulations and directives, based ONLY on the context provided.

Guidelines:
1. Answer ONLY based on the information in the provided context.
2. If the context doesn't contain relevant information, admit that you don't have enough information.
3. Do NOT make up or infer information that's not in the context.
4. Provide specific references to the relevant regulation sections.
5. Use clear, concise language appropriate for regulatory queries.
6. Include direct links and references to the original source documents when mentioned in the context.
7. If dates, numbers, or specific requirements are mentioned in the context, include them precisely.
8. Format your answer for clarity with bullet points or paragraphs as appropriate.

Your answer should be specific, qualified, and include direct links to the relevant sections of regulations.
            """
            
            # Prepare the user message
            user_message = f"""
Query: {query}

Context information from regulatory documents:
{context}

Based ONLY on the information provided in the context above, please answer the query. 
Include specific references to the relevant parts of the regulations.
            """
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more accurate responses
                max_tokens=1000
            )
            
            # Extract the answer
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return "I apologize, but I encountered an error while generating an answer. Please try again."
    
    def _extract_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract and format source information from search results.
        
        Args:
            search_results (List[Dict[str, Any]]): Search results to extract sources from
            
        Returns:
            List[Dict[str, Any]]: Formatted sources
        """
        sources = []
        
        for result in search_results:
            metadata = result.get("metadata", {})
            
            source = {
                "filename": metadata.get("filename", "Unknown"),
                "document_type": metadata.get("document_type", "Unknown"),
                "publication_date": metadata.get("publication_date", "Unknown"),
                "publisher": metadata.get("publisher", "Unknown"),
                "section": metadata.get("section_header", "General"),
                "relevance_score": 1.0 - (result.get("distance", 0) if result.get("distance") is not None else 0)
            }
            
            sources.append(source)
        
        return sources 