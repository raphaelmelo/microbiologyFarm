# Microbiology Farm: PMC Article Scraper

This project scrapes the main content of articles from PubMed Central (PMC) using a CSV with Title and Link columns (file: `SB_publication_PMC.csv`). It downloads each article page and extracts the primary article body text efficiently using async HTTP.

## What it does
- Reads `SB_publication_PMC.csv` (columns: `Title`, `Link`)
- Visits each PMC article page (e.g., `https://www.ncbi.nlm.nih.gov/pmc/articles/PMCXXXXXX/`)
- Extracts the main article body from the page DOM
- Writes one JSON line per article to `output/pmc_articles_html.jsonl`
- Optionally saves raw HTML and/or plain text files per article
- Supports resume to skip already processed items

## Setup
1. Ensure Python 3.9+ is installed.
2. Install dependencies:
   - In this folder, run your preferred installer for `requirements.txt`.

## Running the Application

This project consists of two parts: a FastAPI backend that provides the AI-powered search, and a Streamlit frontend for the user interface. You need to run both simultaneously.

### 1. Run the FastAPI Backend

In your terminal, start the FastAPI server:

```bash
./.venv/bin/uvicorn main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

### 2. Run the Streamlit Frontend

In a **second terminal**, run the Streamlit app:

```bash
./.venv/bin/streamlit run app.py
```

This will open a new tab in your browser with the user interface, typically at `http://localhost:8501`.

You can now ask questions through the Streamlit interface.

## Usage
Basic run (scrape all rows with default concurrency):
- python scripts/scrape_pmc_html.py SB_publication_PMC.csv

Recommended with resume and artifacts:
- python scripts/scrape_pmc_html.py SB_publication_PMC.csv --resume --save-text --save-html --concurrency 12

Options
- --outdir DIR: Output directory (default: `output`)
- --limit N: Process only the first N rows
- --start N: Skip the first N rows
- --concurrency N: Number of concurrent requests (default: 10)
- --save-html: Save raw HTML snapshots to `output/html/`
- --save-text: Save extracted text to `output/text/`
- --resume: Skip PMCIDs already present in the JSONL

Outputs
- output/pmc_articles_html.jsonl: JSON Lines, one record per article { pmcid, source_url, input_title, title, abstract, text, metadata }
- output/html/PMCXXXXXX.html: Optional raw HTML snapshot
- output/text/PMCXXXXXX.txt: Optional extracted text
- output/failures.log: Any failed fetches with error message

## Quick validation
- Try a short run first:
  - python scripts/scrape_pmc_html.py SB_publication_PMC.csv --limit 5 --concurrency 6 --save-text --resume
- You can interrupt and resume later; already-saved PMCIDs will be skipped with `--resume`.

## Notes and etiquette
- Keep concurrency modest (8–16) to be polite to PMC.
- The scraper uses retries with exponential backoff for transient errors.
- DOM shapes can vary slightly across journals. The parser targets the standard PMC main body and falls back to common containers.
