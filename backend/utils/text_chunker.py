from typing import List, Dict, Any
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextChunker:
    """
    A utility class for chunking text into smaller pieces
    for processing and embedding.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        length_function = len
    ):
        """
        Initialize the text chunker with specified parameters.
        
        Args:
            chunk_size (int): Target size of each text chunk
            chunk_overlap (int): Overlap between consecutive chunks
            length_function: Function to determine the length of text chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function
        
        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.length_function,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def identify_section_headers(self, text: str) -> List[str]:
        """
        Identify potential section headers in the text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            List[str]: Identified section headers
        """
        # Common patterns for section headers in regulatory documents
        patterns = [
            r"^Article \d+.*?$",
            r"^Chapter \d+.*?$",
            r"^Section \d+.*?$",
            r"^Annex \d+.*?$",
            r"^\d+\.\d+(\.\d+)* .*?$"  # Hierarchical numbering like 1.2.3
        ]
        
        headers = []
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if line and any(re.match(pattern, line, re.MULTILINE) for pattern in patterns):
                headers.append(line)
        
        return headers
    
    def split_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks with associated metadata.
        
        Args:
            text (str): The text to chunk
            metadata (Dict[str, Any], optional): Metadata to associate with chunks
            
        Returns:
            List[Dict[str, Any]]: List of chunks with metadata
        """
        if not text:
            return []
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Identify section headers for context
        section_headers = self.identify_section_headers(text)
        
        result = []
        
        for i, chunk in enumerate(chunks):
            # Create chunk metadata
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata.update({
                "chunk_id": i,
                "chunk_index": i,
                "chunk_count": len(chunks)
            })
            
            # Find relevant section headers for this chunk
            # (simplified approach - can be improved)
            chunk_text_position = text.find(chunk)
            if chunk_text_position >= 0:
                relevant_headers = []
                text_before_chunk = text[:chunk_text_position]
                
                for header in section_headers:
                    if header in text_before_chunk:
                        relevant_headers.append(header)
                
                if relevant_headers:
                    chunk_metadata["section_header"] = relevant_headers[-1]
            
            result.append({
                "content": chunk,
                "metadata": chunk_metadata
            })
        
        return result
    
    def process_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a document dictionary and split its content into chunks.
        
        Args:
            document (Dict[str, Any]): Document with content and metadata
            
        Returns:
            List[Dict[str, Any]]: List of chunks with metadata
        """
        if "content" not in document or not document["content"]:
            return []
        
        return self.split_text(
            text=document["content"],
            metadata=document.get("metadata", {})
        ) 