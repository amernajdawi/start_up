import os
import re
import sys
import argparse
from pathlib import Path
import PyPDF2
import time
import math

def detect_table(text):
    """
    Detect if the text contains a table structure.
    Simple heuristic: looks for repeated patterns of whitespace that might indicate columns.
    """
    # Look for repeated pipe characters, which often indicate table columns
    if '|' in text:
        return True
    
    # Look for patterns of spaces that might indicate table structure
    lines = text.split('\n')
    if len(lines) > 3:  # Need multiple lines to detect a table
        # Check if multiple lines have similar spacing patterns
        space_patterns = []
        for line in lines:
            # Create a pattern where spaces are marked as 'S' and non-spaces as 'C'
            pattern = ''.join(['S' if c.isspace() else 'C' for c in line])
            # Compress repeated characters
            compressed = re.sub(r'(S|C)\1+', r'\1', pattern)
            if compressed and 'S' in compressed:
                space_patterns.append(compressed)
        
        # If we have similar patterns repeating, it might be a table
        if len(space_patterns) > 3:
            pattern_counts = {}
            for pattern in space_patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            # If any pattern appears multiple times, likely a table
            for count in pattern_counts.values():
                if count >= 3:
                    return True
    
    return False

def preserve_table_structure(text):
    """
    Try to preserve table structure by maintaining spacing and alignment.
    """
    lines = text.split('\n')
    preserved_lines = []
    
    for line in lines:
        # Don't compress whitespace in lines that seem to be part of tables
        if re.search(r'\s{2,}', line):  # Multiple spaces might indicate table columns
            preserved_lines.append(line)
        else:
            # For non-table text, normalize whitespace
            preserved_lines.append(re.sub(r'\s+', ' ', line).strip())
    
    return '\n'.join(preserved_lines)

def extract_text_from_pdf(pdf_path, detect_tables=True):
    """Extract text from a PDF file with improved formatting and table detection."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            total_pages = len(reader.pages)
            
            # Process each page
            for page_num in range(total_pages):
                page_text = reader.pages[page_num].extract_text()
                
                # Check if page might contain tables
                has_table = detect_tables and detect_table(page_text)
                
                if has_table:
                    # Preserve spacing for table structure
                    page_text = preserve_table_structure(page_text)
                else:
                    # Clean up text: remove excessive whitespace
                    page_text = re.sub(r'\s+', ' ', page_text)
                
                # Add page number for reference
                text += f"\n--- Page {page_num + 1} of {total_pages} ---\n\n"
                text += page_text + '\n'
            
            return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def count_tokens(text):
    """
    Count tokens in text more accurately.
    
    This is a simple approximation of token counting.
    A more accurate method would use a tokenizer from a library like transformers,
    but this avoids adding dependencies.
    """
    # Split on whitespace and punctuation
    tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
    return len(tokens)

def split_text_into_chunks(text, chunk_size=500, overlap=50):
    """
    Split text into chunks of approximately chunk_size tokens with optional overlap.
    
    Args:
        text: The text to split
        chunk_size: Target size of each chunk in tokens
        overlap: Number of tokens to overlap between chunks
    """
    # Split the text by paragraphs or lines
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = ""
    current_chunk_tokens = 0
    
    for paragraph in paragraphs:
        # Detect if paragraph is likely a table
        is_table = detect_table(paragraph)
        
        # Count tokens in this paragraph
        paragraph_tokens = count_tokens(paragraph)
        
        # For tables or very long paragraphs, we might want to keep them intact
        # if possible, or split at a logical point
        if is_table and paragraph_tokens > chunk_size:
            # If we already have content in the current chunk, save it first
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_chunk_tokens = 0
            
            # Split the table by lines to preserve its structure as much as possible
            table_lines = paragraph.split('\n')
            table_chunk = ""
            table_chunk_tokens = 0
            
            for line in table_lines:
                line_tokens = count_tokens(line)
                
                if table_chunk_tokens + line_tokens > chunk_size and table_chunk:
                    chunks.append(table_chunk.strip())
                    table_chunk = line
                    table_chunk_tokens = line_tokens
                else:
                    if table_chunk:
                        table_chunk += "\n" + line
                    else:
                        table_chunk = line
                    table_chunk_tokens += line_tokens
            
            if table_chunk:
                chunks.append(table_chunk.strip())
            
            continue
        
        # If adding this paragraph would exceed the chunk size and we already have content,
        # start a new chunk
        if current_chunk_tokens + paragraph_tokens > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # If overlap is enabled, keep some of the previous chunk
            if overlap > 0 and current_chunk and not is_table:
                # Split the current chunk into tokens
                all_tokens = re.findall(r'\b\w+\b|[^\w\s]', current_chunk)
                
                # Take the last 'overlap' tokens if we have that many
                overlap_tokens = min(overlap, len(all_tokens))
                
                # Rejoin the overlap tokens into text
                if overlap_tokens > 0:
                    overlap_text = " ".join(all_tokens[-overlap_tokens:])
                    current_chunk = overlap_text + "\n\n" + paragraph
                    current_chunk_tokens = count_tokens(current_chunk)
                else:
                    current_chunk = paragraph
                    current_chunk_tokens = paragraph_tokens
            else:
                current_chunk = paragraph
                current_chunk_tokens = paragraph_tokens
        else:
            # Add to the current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
            
            current_chunk_tokens = count_tokens(current_chunk)
    
    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def pdf_to_text_chunked(chunk_size=500, overlap=50, detect_tables=True):
    """
    Convert all PDFs to text files and split into chunks.
    
    Args:
        chunk_size: Target size of each chunk in tokens
        overlap: Number of tokens to overlap between chunks
        detect_tables: Whether to detect and preserve table structures
    """
    start_time = time.time()
    
    # Get the script directory
    script_dir = Path(__file__).parent.absolute()
    
    # Use relative paths based on the script's location
    # Look for PDFs in a 'data' directory at the same level as the 'backend' directory
    pdf_dir = script_dir.parent / 'data'
    # Output to a 'text_output' directory at the same level as the 'backend' directory
    output_dir = script_dir.parent / 'text_output'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Looking for PDFs in: {pdf_dir}")
    print(f"Output directory: {output_dir}")
    
    # Get all PDF files
    pdf_files = list(pdf_dir.glob('*.pdf'))
    total_files = len(pdf_files)
    print(f"Found {total_files} PDF files")
    print(f"Using chunk size of {chunk_size} tokens with {overlap} tokens overlap")
    print(f"Table detection: {'Enabled' if detect_tables else 'Disabled'}")
    
    successful = 0
    failed = 0
    total_chunks = 0
    
    for i, pdf_path in enumerate(pdf_files, 1):
        try:
            # Extract text from PDF
            file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
            print(f"[{i}/{total_files}] Processing: {pdf_path.name} ({file_size_mb:.2f} MB)")
            
            text = extract_text_from_pdf(pdf_path, detect_tables)
            
            # Create metadata header
            metadata = f"File Name: {pdf_path.name}\n"
            metadata += f"Converted on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            metadata += f"Original Size: {file_size_mb:.2f} MB\n"
            metadata += f"Chunk Size: {chunk_size} tokens with {overlap} tokens overlap\n"
            metadata += f"Table Detection: {'Enabled' if detect_tables else 'Disabled'}\n"
            metadata += "-" * 80 + "\n\n"
            
            # Split text into chunks
            chunks = split_text_into_chunks(text, chunk_size, overlap)
            file_chunks = len(chunks)
            total_chunks += file_chunks
            
            # Save each chunk to a separate file
            for chunk_num, chunk in enumerate(chunks, 1):
                # Create output filename with chunk number
                output_filename = f"{pdf_path.stem}_chunk{chunk_num:03d}.txt"
                output_path = output_dir / output_filename
                
                # Write chunk to file
                with open(output_path, 'w', encoding='utf-8') as f:
                    # Add metadata and chunk information
                    f.write(metadata)
                    f.write(f"Chunk: {chunk_num} of {file_chunks}\n")
                    f.write("-" * 80 + "\n\n")
                    f.write(chunk)
            
            successful += 1
            print(f"✓ Successfully converted {pdf_path.name} to {file_chunks} chunks")
            
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
    print(f"Total chunks created: {total_chunks}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"All chunked text files saved to {output_dir}")
    print("="*50)

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Convert PDFs to chunked text files')
    parser.add_argument('--chunk-size', type=int, default=500,
                        help='Target size of each chunk in tokens (default: 500)')
    parser.add_argument('--overlap', type=int, default=50,
                        help='Number of tokens to overlap between chunks (default: 50)')
    parser.add_argument('--no-tables', action='store_true',
                        help='Disable table detection and preservation')
    parser.add_argument('--pdf-dir', type=str, 
                        help='Directory containing PDF files (default: ../data)')
    parser.add_argument('--output-dir', type=str,
                        help='Directory for output text files (default: ../text_output)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Override default directories if provided via command line
    if args.pdf_dir or args.output_dir:
        # Get the script directory
        script_dir = Path(__file__).parent.absolute()
        
        # Use provided directories or defaults
        pdf_dir = Path(args.pdf_dir) if args.pdf_dir else script_dir.parent / 'data'
        output_dir = Path(args.output_dir) if args.output_dir else script_dir.parent / 'text_output'
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Looking for PDFs in: {pdf_dir}")
        print(f"Output directory: {output_dir}")
        
        # Get all PDF files
        pdf_files = list(pdf_dir.glob('*.pdf'))
        
        # Custom function to handle specified directories
        custom_pdf_to_text_chunked(pdf_dir, output_dir, pdf_files, args.chunk_size, args.overlap, not args.no_tables)
    else:
        # Run the converter with default paths
        pdf_to_text_chunked(args.chunk_size, args.overlap, not args.no_tables)

def custom_pdf_to_text_chunked(pdf_dir, output_dir, pdf_files, chunk_size=500, overlap=50, detect_tables=True):
    """
    Convert PDFs to text files with custom input and output directories.
    """
    start_time = time.time()
    
    total_files = len(pdf_files)
    print(f"Found {total_files} PDF files")
    print(f"Using chunk size of {chunk_size} tokens with {overlap} tokens overlap")
    print(f"Table detection: {'Enabled' if detect_tables else 'Disabled'}")
    
    successful = 0
    failed = 0
    total_chunks = 0
    
    for i, pdf_path in enumerate(pdf_files, 1):
        try:
            # Extract text from PDF
            file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
            print(f"[{i}/{total_files}] Processing: {pdf_path.name} ({file_size_mb:.2f} MB)")
            
            text = extract_text_from_pdf(pdf_path, detect_tables)
            
            # Create metadata header
            metadata = f"File Name: {pdf_path.name}\n"
            metadata += f"Converted on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            metadata += f"Original Size: {file_size_mb:.2f} MB\n"
            metadata += f"Chunk Size: {chunk_size} tokens with {overlap} tokens overlap\n"
            metadata += f"Table Detection: {'Enabled' if detect_tables else 'Disabled'}\n"
            metadata += "-" * 80 + "\n\n"
            
            # Split text into chunks
            chunks = split_text_into_chunks(text, chunk_size, overlap)
            file_chunks = len(chunks)
            total_chunks += file_chunks
            
            # Save each chunk to a separate file
            for chunk_num, chunk in enumerate(chunks, 1):
                # Create output filename with chunk number
                output_filename = f"{pdf_path.stem}_chunk{chunk_num:03d}.txt"
                output_path = output_dir / output_filename
                
                # Write chunk to file
                with open(output_path, 'w', encoding='utf-8') as f:
                    # Add metadata and chunk information
                    f.write(metadata)
                    f.write(f"Chunk: {chunk_num} of {file_chunks}\n")
                    f.write("-" * 80 + "\n\n")
                    f.write(chunk)
            
            successful += 1
            print(f"✓ Successfully converted {pdf_path.name} to {file_chunks} chunks")
            
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
    print(f"Total chunks created: {total_chunks}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"All chunked text files saved to {output_dir}")
    print("="*50)

if __name__ == "__main__":
    main() 