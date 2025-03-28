# PDF to Text Converter with Chunking

This script converts PDF files from the `/app/data` directory to chunked text files, splitting each document into segments of approximately 500 tokens each, with special handling for complex tables and multi-page layouts.

## Features

- Processes all PDF files in the `/app/data` directory
- Preserves the original naming convention with chunk numbering
- Splits text into manageable chunks with customizable size
- Adds token overlap between chunks for better context continuity
- **Detects and preserves table structures** for better readability
- **Special handling for complex document layouts**
- Outputs chunked text files to `/app/text_output` directory
- Adds metadata and chunk information to each file
- Handles errors gracefully

## How to Use

1. Make sure all your PDF files are in the `/app/data` directory
2. Ensure the output directory `/app/text_output` exists (it will be created if it doesn't)
3. Run the script using Poetry:

```bash
# Basic usage with default settings (500 tokens per chunk, 50 tokens overlap)
cd /app/backend
poetry run python pdf_to_text_chunked.py

# Custom chunk size and overlap
poetry run python pdf_to_text_chunked.py --chunk-size 800 --overlap 100

# Disable table detection if needed
poetry run python pdf_to_text_chunked.py --no-tables
```

4. The chunked text files will be saved in `/app/text_output`

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--chunk-size` | Target size of each chunk in tokens | 500 |
| `--overlap` | Number of tokens to overlap between chunks | 50 |
| `--no-tables` | Disable table structure detection and preservation | False (tables enabled) |

## Table Handling

The script includes special handling for tables:

1. **Table Detection** - Automatically identifies tabular content by analyzing spacing patterns and structural indicators
2. **Structure Preservation** - Maintains column alignment and spacing in table content
3. **Smart Chunking** - Tables are kept intact where possible, or split along logical boundaries
4. **Line-by-Line Processing** - For large tables that exceed chunk size, splitting occurs at line boundaries to preserve structure

## Output File Naming Convention

The script preserves the original PDF filename and adds chunk numbering:

`{original_filename_without_extension}_chunk{chunk_number}.txt`

For example, `1_2020-06-18_VO_2020_852_TAXAllg_EU.pdf` becomes:
- `1_2020-06-18_VO_2020_852_TAXAllg_EU_chunk001.txt`
- `1_2020-06-18_VO_2020_852_TAXAllg_EU_chunk002.txt`
- ... and so on

## Chunk Size and Overlapping

- The default chunk size is approximately 500 tokens
- Chunks have a 50-token overlap by default to maintain context between chunks
- The chunking algorithm tries to preserve paragraph boundaries
- Tables are handled specially to maintain their structure
- Each chunk contains metadata about the source file and its position in the sequence

## Token Counting

The script uses a simple token counting algorithm that approximates the tokenization process of language models. It counts:
- Words (sequences of word characters)
- Punctuation marks
- Special characters

## Use Cases

Chunked text files are useful for:
- Processing with AI models that have token limits
- More efficient document retrieval and search
- Easier management of large text documents
- Parallel processing of document segments
- Working with document collections containing complex tables and layouts 