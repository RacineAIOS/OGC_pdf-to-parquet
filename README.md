# OGC_pdf-to-parquet

A tool for converting technical PDF documents into a dataset of query-image pairs stored in Parquet format. This project processes PDFs, renders pages as images, extracts text, generates technical queries using Gemini AI, and stores everything in Parquet files suitable for machine learning applications.

## Examples of datasets created with this method

https://huggingface.co/racineai

## Overview

OGC_pdf-to-parquet helps create specialized technical datasets by:

1. Converting PDF pages to high-quality images
2. Using Gemini AI to generate four types of technical queries for each page:
   - Main technical queries
   - Secondary technical queries
   - Visual element queries
   - Complex multimodal semantic queries
3. Detecting the document language
4. Saving the query-image pairs as Parquet files


### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/OGC_pdf-to-parquet.git
   cd OGC_pdf-to-parquet
   ```

2. Install dependencies

3. Create a `.env` file with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

## Configuration

The project is configured through `config.py`. Key settings include:

| Setting | Description | Default |
|---------|-------------|---------|
| `PARALLEL_INSTANCES` | Number of parallel API instances | 40 |
| `REQUESTS_PER_SECOND` | Rate limit for API calls | 40 |
| `GEMINI_MODEL` | Gemini model to use | "openrouter/google/gemini-2.0-flash-lite-001" |
| `ZOOM_FACTOR` | Image quality factor (higher = better quality) | 1.5 |
| `CHUNK_SIZE` | Number of PDF pages to process in parallel | 40 |
| `INPUT_FOLDER` | Folder containing input PDFs | "Test" |
| `OUTPUT_FOLDER` | Folder for output Parquet files | "out_test" |
| `PARQUET_SIZE` | Number of entries per Parquet file | 1420 |
| `FILE_NAMES` | Prefix for output files ("train" or "test") | "train" |

Adjust these settings based on your needs and the API rate limits.

## Usage

1. Place your PDF files in the configured input folder (default: `Test/`)

2. Run the main script:
   ```
   python main.py
   ```

3. (Optional) To rename the output files with sequential numbering:
   ```
   python rename.py
   ```

## How It Works

### Process Flow

1. **PDF Processing**: Each PDF is loaded and processed page by page
2. **Image & Text Extraction**: Pages are rendered as high-quality images
3. **Query Generation**: The Gemini API analyzes each page to generate specialized queries
4. **Language Detection**: The system detects the primary language of each document
5. **Parquet Storage**: Generated query-image pairs are saved in Parquet format

### Generated Query Types

The system generates four distinct query types for each page:

- **Main Query**: Core technical specifications and information
- **Secondary Query**: Detailed technical aspects and specific details
- **Visual Query**: Queries related to diagrams and visual elements
- **Multimodal Query**: Complex semantic search queries combining multiple aspects

## Advanced Configuration

### Rate Limiting

The `RateLimiter` class manages API call frequency. Adjust `REQUESTS_PER_SECOND` in `config.py` to comply with your API provider's limits.

### Concurrency

Processing uses asyncio for concurrency:
- `PARALLEL_INSTANCES`: Number of parallel API clients
- `CHUNK_SIZE`: Number of PDF pages processed in parallel
- `concurrency_limit` in `main.py`: Limits PDF processing concurrency

## Troubleshooting

### API Rate Limits

If encountering rate limit errors:
1. Reduce `REQUESTS_PER_SECOND` in `config.py`
2. Reduce `PARALLEL_INSTANCES` for fewer concurrent API calls

### Memory Issues

For large PDFs or memory constraints:
1. Reduce `CHUNK_SIZE` to process fewer pages simultaneously
2. Process PDFs in smaller batches by moving files to the input directory in stages

### Output File Naming

The default naming scheme creates files like `train-00000-of-n.parquet`. To rename to a consistent scheme:
1. Complete the processing run
2. Edit the total count in `rename.py` if needed
3. Run `python rename.py` to rename files

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.




## Author

Léo Appourchaux - AI DEV at TW3/Racine.ai
- https://huggingface.co/Leo-D-M-Appourchaux
- https://github.com/Leo-D-M-Appourchaux
