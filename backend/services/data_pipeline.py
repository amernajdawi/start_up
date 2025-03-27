import os
from typing import Dict, List, Any, Optional
import json
from tqdm import tqdm

from backend.utils.pdf_processor import PDFProcessor
from backend.utils.text_chunker import TextChunker
from backend.utils.embeddings_generator import EmbeddingsGenerator
from backend.services.vector_store import VectorStore

class DataPipeline:
    """
    A service class for running the data processing pipeline:
    1. Extract text from PDFs
    2. Chunk the text into smaller pieces
    3. Generate embeddings for each chunk
    4. Store the chunks and embeddings in a vector database
    """
    
    def __init__(
        self,
        data_dir: str = "../data",
        persist_dir: str = "./chroma_db",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        api_key: str = None
    ):
        """
        Initialize the data pipeline with specified parameters.
        
        Args:
            data_dir (str): Directory containing PDF files
            persist_dir (str): Directory to persist the vector database
            chunk_size (int): Size of text chunks
            chunk_overlap (int): Overlap between consecutive chunks
            api_key (str, optional): OpenAI API key (defaults to environment variable)
        """
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        
        # Initialize components
        self.pdf_processor = PDFProcessor(data_dir=data_dir)
        self.text_chunker = TextChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embeddings_generator = EmbeddingsGenerator(api_key=api_key)
        self.vector_store = VectorStore(persist_directory=persist_dir)
        
        # Create intermediate directories for debugging if needed
        os.makedirs("./temp", exist_ok=True)
    
    def run_pipeline(self, save_intermediates: bool = False) -> Dict[str, Any]:
        """
        Run the complete data processing pipeline.
        
        Args:
            save_intermediates (bool): Whether to save intermediate results
            
        Returns:
            Dict[str, Any]: Pipeline statistics
        """
        # Step 1: Process PDFs and extract text
        print("Step 1: Processing PDFs and extracting text...")
        documents = self.pdf_processor.process_all_pdfs()
        
        if save_intermediates:
            with open("./temp/documents.json", "w") as f:
                # Create a serializable version of the documents
                serializable_docs = {}
                for doc_id, doc in documents.items():
                    serializable_doc = doc.copy()
                    # Truncate content for readability in debug file
                    serializable_doc["content"] = doc["content"][:500] + "..." if doc["content"] else ""
                    serializable_docs[doc_id] = serializable_doc
                json.dump(serializable_docs, f, indent=2)
        
        # Step 2: Chunk the documents
        print("Step 2: Chunking documents...")
        all_chunks = []
        
        for doc_id, document in tqdm(documents.items()):
            chunks = self.text_chunker.process_document(document)
            all_chunks.extend(chunks)
            
        print(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        
        if save_intermediates:
            with open("./temp/chunks.json", "w") as f:
                # Create a serializable version of the chunks
                serializable_chunks = []
                for i, chunk in enumerate(all_chunks[:10]):  # Save only first 10 for readability
                    serializable_chunk = chunk.copy()
                    serializable_chunks.append(serializable_chunk)
                json.dump(serializable_chunks, f, indent=2)
        
        # Step 3: Generate embeddings for chunks
        print("Step 3: Generating embeddings...")
        chunks_with_embeddings = self.embeddings_generator.process_chunks(all_chunks)
        
        if save_intermediates:
            with open("./temp/embeddings_info.json", "w") as f:
                embedding_info = {
                    "total_chunks": len(chunks_with_embeddings),
                    "embedding_dimensions": len(chunks_with_embeddings[0]["embedding"]) if chunks_with_embeddings else 0,
                    "sample_chunk": {
                        "content": chunks_with_embeddings[0]["content"][:200] + "..." if chunks_with_embeddings else "",
                        "embedding_preview": str(chunks_with_embeddings[0]["embedding"][:5]) + "..." if chunks_with_embeddings else ""
                    }
                }
                json.dump(embedding_info, f, indent=2)
        
        # Step 4: Store chunks and embeddings in vector database
        print("Step 4: Storing chunks in vector database...")
        self.vector_store.add_chunks(chunks_with_embeddings)
        
        # Get collection stats
        stats = self.vector_store.get_collection_stats()
        
        # Return pipeline statistics
        return {
            "documents_processed": len(documents),
            "chunks_created": len(all_chunks),
            "embeddings_generated": len(chunks_with_embeddings),
            "vector_store_stats": stats
        }
    
    def process_single_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single document through the pipeline.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict[str, Any]: Processing statistics
        """
        if not os.path.exists(file_path) or not file_path.lower().endswith('.pdf'):
            return {"error": f"Invalid file path or not a PDF: {file_path}"}
        
        # Extract the filename
        filename = os.path.basename(file_path)
        
        # Step 1: Process PDF and extract text
        metadata = self.pdf_processor.extract_metadata_from_filename(filename)
        text_content = self.pdf_processor.extract_text(file_path)
        
        document = {
            "metadata": metadata,
            "content": text_content,
            "path": file_path
        }
        
        # Step 2: Chunk the document
        chunks = self.text_chunker.process_document(document)
        
        # Step 3: Generate embeddings for chunks
        chunks_with_embeddings = self.embeddings_generator.process_chunks(chunks)
        
        # Step 4: Store chunks and embeddings in vector database
        self.vector_store.add_chunks(chunks_with_embeddings)
        
        # Return processing statistics
        return {
            "filename": filename,
            "chunks_created": len(chunks),
            "embeddings_generated": len(chunks_with_embeddings)
        } 