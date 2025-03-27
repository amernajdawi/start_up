import os
import PyPDF2
from typing import Dict, List, Optional
import re
from tqdm import tqdm

class PDFProcessor:
    """
    A utility class for processing PDF files and extracting text content.
    """
    
    def __init__(self, data_dir: str):
        """
        Initialize the PDF processor with the directory containing PDF files.
        
        Args:
            data_dir (str): Path to the directory containing PDF files
        """
        self.data_dir = data_dir
        self.pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith('.pdf')]
    
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, str]:
        """
        Extract metadata from the filename based on the provided schema.
        
        Example: "1_2023-07-31_DelVO_2023/2772_ESRS_EU"
        
        Args:
            filename (str): The filename to parse
            
        Returns:
            Dict[str, str]: Extracted metadata
        """
        metadata = {
            "filename": filename,
            "hierarchy_level": None,
            "publication_date": None,
            "document_type": None,
            "designation": None,
            "abbreviation": None,
            "publisher": None
        }
        
        # Remove .pdf extension
        basename = os.path.splitext(filename)[0]
        
        # Split the components
        parts = basename.split('_')
        
        if len(parts) >= 1:
            metadata["hierarchy_level"] = parts[0]
            
        if len(parts) >= 2 and re.match(r'\d{4}-\d{2}-\d{2}', parts[1]):
            metadata["publication_date"] = parts[1]
            
        if len(parts) >= 3:
            metadata["document_type"] = parts[2]
            
        if len(parts) >= 4 and '/' in parts[3]:
            # Handle designation with slash notation (e.g., "2023/2772")
            metadata["designation"] = parts[3].replace('/', '_')
        elif len(parts) >= 4:
            metadata["designation"] = parts[3]
            
        if len(parts) >= 5:
            metadata["abbreviation"] = parts[4]
            
        if len(parts) >= 6:
            metadata["publisher"] = parts[5]
            
        return metadata
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text content
        """
        text = ""
        
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text:
                        text += page_text + "\n\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    def process_all_pdfs(self) -> Dict[str, Dict]:
        """
        Process all PDF files in the data directory and extract text content.
        
        Returns:
            Dict[str, Dict]: Dictionary mapping file IDs to their metadata and content
        """
        result = {}
        
        print(f"Processing {len(self.pdf_files)} PDF files...")
        
        for filename in tqdm(self.pdf_files):
            file_path = os.path.join(self.data_dir, filename)
            metadata = self.extract_metadata_from_filename(filename)
            text_content = self.extract_text(file_path)
            
            # Create a unique ID for the document
            doc_id = os.path.splitext(filename)[0]
            
            result[doc_id] = {
                "metadata": metadata,
                "content": text_content,
                "path": file_path
            }
            
        return result 