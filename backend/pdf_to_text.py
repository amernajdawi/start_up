import os
import re
from pathlib import Path
import PyPDF2
import time

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file with improved formatting."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            total_pages = len(reader.pages)
            
            # Process each page
            for page_num in range(total_pages):
                page_text = reader.pages[page_num].extract_text()
                
                # Clean up text: remove excessive whitespace
                page_text = re.sub(r'\s+', ' ', page_text)
                
                # Add page number for reference
                text += f"\n--- Page {page_num + 1} of {total_pages} ---\n\n"
                text += page_text + '\n'
            
            return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def pdf_to_text():
    """Convert all PDFs in the data directory to text files with better formatting and error handling."""
    start_time = time.time()
    pdf_dir = Path('/app/data')
    output_dir = Path('/app/data/text_output')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all PDF files
    pdf_files = list(pdf_dir.glob('*.pdf'))
    total_files = len(pdf_files)
    print(f"Found {total_files} PDF files")
    
    successful = 0
    failed = 0
    
    for i, pdf_path in enumerate(pdf_files, 1):
        try:
            # Extract text from PDF
            file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
            print(f"[{i}/{total_files}] Processing: {pdf_path.name} ({file_size_mb:.2f} MB)")
            
            text = extract_text_from_pdf(pdf_path)
            
            # Create output filename (same as PDF but with .txt extension)
            output_path = output_dir / f"{pdf_path.stem}.txt"
            
            # Write text to file
            with open(output_path, 'w', encoding='utf-8') as f:
                # Add metadata header
                f.write(f"File Name: {pdf_path.name}\n")
                f.write(f"Converted on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Original Size: {file_size_mb:.2f} MB\n")
                f.write("-" * 80 + "\n\n")
                f.write(text)
                
            successful += 1
            print(f"✓ Successfully converted {pdf_path.name} to {output_path.name}")
        except Exception as e:
            failed += 1
            print(f"✗ Error processing {pdf_path.name}: {str(e)}")
    
    # Print summary
    elapsed_time = time.time() - start_time
    print("\n" + "="*50)
    print(f"Conversion Summary:")
    print(f"Total files: {total_files}")
    print(f"Successful conversions: {successful}")
    print(f"Failed conversions: {failed}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"All text files saved to {output_dir}")
    print("="*50)

if __name__ == "__main__":
    pdf_to_text() 