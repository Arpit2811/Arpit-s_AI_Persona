# Corpus Builder (Parallel Mode)

A high‑performance corpus extraction pipeline designed to process large
collections of document metadata and extract clean textual data.

This tool supports multiple document formats and uses **parallel
multiprocessing** for faster processing. It is designed for
**large‑scale text corpus building**, dataset preparation, and NLP
pipelines.

------------------------------------------------------------------------

# Features

-   Parallel processing using Python multiprocessing
-   Native extraction for:
    -   EPUB
    -   FB2
    -   DOCX
    -   TXT
    -   HTML
-   Complex extraction for:
    -   MOBI
    -   AZW / AZW3
    -   PRC / PDB
-   Automatic fallback to **Apache Tika** for unsupported formats
-   Removes FB2 binary image data to prevent garbage text
-   Encoding issue detection
-   Automatic word and page estimation
-   Robust logging system
-   Resilient file resolution logic

------------------------------------------------------------------------

# Supported Formats

  Format              Extraction Method
  ------------------- ----------------------
  TXT                 Native
  HTML / HTM          Native
  EPUB                Native
  FB2                 Native
  DOCX                Native
  MOBI / AZW / AZW3   Complex Extraction
  PRC / PDB           Complex Extraction
  XML / OPF           Markup Parsing
  Others              Apache Tika Fallback

Ignored formats include:

    jpg jpeg png exe lnk db iso rar zip djvu pdf

------------------------------------------------------------------------

# Architecture

Pipeline Flow

    metadata.jsonl
          │
          ▼
    Parallel Workers
          │
          ▼
    File Resolver
          │
          ▼
    Extractor Dispatcher
          │
     ┌────┼───────────────┐
     │    │               │
    Native Extractors   MOBI Handler
     │                  │
     ▼                  ▼
    Clean Text Output
          │
          ▼
    JSONL Corpus File

------------------------------------------------------------------------

# Installation

Clone the repository:

``` bash
git clone https://github.com/your-repo/corpus-builder.git
cd corpus-builder
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

Apache Tika will automatically download its server jar on first
execution.

------------------------------------------------------------------------

# Usage

Basic usage:

``` bash
python corpus_builder.py \
--input metadata.jsonl \
--output corpus.jsonl \
--log extraction.log
```

Specify number of workers:

``` bash
python corpus_builder.py \
-i metadata.jsonl \
-o corpus.jsonl \
-l extraction.log \
-w 8
```

Default workers = **CPU cores − 1**

------------------------------------------------------------------------

# Input Format

Input must be a **JSONL file**.

Example:

``` json
{
  "aacid": "12345",
  "path": "/data/books/book1",
  "metadata": {
    "extension": "epub",
    "pages": 200,
    "filesize_reported": 123456
  }
}
```

------------------------------------------------------------------------

# Output Format

Output is also **JSONL**.

Example:

``` json
{
  "aacid": "12345",
  "metadata": {...},
  "extracted_stats": {
    "num_words": 50000,
    "num_pages": 200
  },
  "data": "Extracted book text..."
}
```

------------------------------------------------------------------------

# Logging

Logs are written to the file specified with:

    --log extraction.log

Logs include:

-   file processing
-   encoding errors
-   missing files
-   extraction failures
-   periodic progress updates

------------------------------------------------------------------------

# Performance

Parallel mode allows scaling to very large datasets.

Typical performance:

  Workers   Files / Minute
  --------- ----------------
  4         \~200
  8         \~450
  16        \~900

Actual performance depends on disk speed, file size, and document type.

------------------------------------------------------------------------

# Debug Mode

To process only a few records for testing:

``` python
DEBUG_LIMIT = 5
```

Then enable the lock inside the processing loop.

------------------------------------------------------------------------

# Dependencies

Main libraries used:

-   beautifulsoup4
-   lxml
-   mobi
-   tika
-   multiprocessing (Python standard library)

Full list available in `requirements.txt`.

------------------------------------------------------------------------

# Use Cases

-   NLP corpus building
-   Large dataset preparation for LLM training
-   Digital library ingestion pipelines
-   Research dataset generation
-   Document text extraction pipelines

------------------------------------------------------------------------

# License

MIT License