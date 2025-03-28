# PDF Text Extraction Tools

This repository contains two Python scripts for converting PDF files to text:

1. **pdf_to_text.py** - Converts PDFs to text files (one file per PDF)
2. **pdf_to_text_chunked.py** - Converts PDFs to chunked text files (multiple files per PDF)

Both scripts preserve the original naming convention of the PDF files and add helpful metadata.

## Usage Instructions

### Basic Text Extraction

To convert PDFs to full text files:

```bash
cd /app/backend
poetry run python pdf_to_text.py
```

Output will be saved to `/app/data/text_output` with each PDF converted to a single text file.

### Chunked Text Extraction

To convert PDFs to chunked text files (better for processing with AI models):

```bash
cd /app/backend
# Default settings (500 tokens per chunk, 50 tokens overlap)
poetry run python pdf_to_text_chunked.py

# Custom settings
poetry run python pdf_to_text_chunked.py --chunk-size 800 --overlap 100
```

Output will be saved to `/app/text_output` with each PDF split into multiple chunks.

## File Naming Convention

Both scripts preserve the original filename pattern:

- Hierarchy Level (e.g., 1, 2)
- Date (e.g., 2020-06-18)
- Document Type (e.g., VO, DelVO, RL, G, REP, E)
- Official EU Designation (e.g., 2020/852)
- Abbreviation (e.g., TAXAllg, ESRS, CSRD)
- Publisher (e.g., EU, WRI&WBCSD)

For example:
- `1_2020-06-18_VO_2020_852_TAXAllg_EU.pdf` → `1_2020-06-18_VO_2020_852_TAXAllg_EU.txt`
- Chunked version: `1_2020-06-18_VO_2020_852_TAXAllg_EU_chunk001.txt`, `1_2020-06-18_VO_2020_852_TAXAllg_EU_chunk002.txt`, etc.

## Features Comparison

| Feature | pdf_to_text.py | pdf_to_text_chunked.py |
|---------|---------------|-----------------------|
| Output format | One text file per PDF | Multiple chunk files per PDF |
| Output location | `/app/data/text_output` | `/app/text_output` |
| Page numbers | Yes | Yes |
| File metadata | Yes | Yes |
| Token chunking | No | Yes (customizable) |
| Chunk overlap | No | Yes (customizable) |
| CLI parameters | No | Yes |

## Requirements

Both scripts require:
- Python 3.9+
- PyPDF2 library (installed via Poetry)

## Detailed Documentation

For more detailed information about each script, please refer to:

- [PDF to Text README](pdf_to_text_README.md)
- [PDF to Text Chunked README](pdf_to_text_chunked_README.md) 