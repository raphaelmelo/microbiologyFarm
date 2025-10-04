# Microbiology Farm: RAG-based Q&A System

This project implements a Retrieval-Augmented Generation (RAG) system to answer questions about a collection of microbiology articles from PubMed Central (PMC). It uses a FastAPI backend for the AI logic and a Streamlit frontend for the user interface.

## What it does
-   **`create_index.py`**: Reads processed article data, generates embeddings using `sentence-transformers`, and builds a FAISS index for efficient similarity search.
-   **`main.py`**: A FastAPI application that exposes an `/ask` endpoint. It takes a user's question, retrieves relevant context from the FAISS index, and uses Google's Gemini model to generate an answer.
-   **`app.py`**: A Streamlit web application that provides a chat interface for users to interact with the backend.

## Setup
1.  Ensure Python 3.9+ is installed.
2.  Create a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `.env` file in the root directory and add your Google API key:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

## Running the Application

### 1. Create the Search Index
First, you need to generate the FAISS index from your article data. Make sure you have the `output/pmc_articles_html.jsonl` file from a previous scraping step.

```bash
python create_index.py
```
This will create the `rag_index` directory containing the `articles.index` and `texts.json` files.

### 2. Run the Application
The `run.sh` script starts both the backend and frontend.

```bash
./run.sh
```
- The FastAPI backend will run on `http://127.0.0.1:8000`.
- The Streamlit frontend will be available at `http://localhost:8501`.

You can now ask questions through the Streamlit interface.

## Docker
You can also run the application using Docker.

1.  Build the Docker image:
    ```bash
    docker build -t microbiology-farm .
    ```
2.  Run the Docker container:
    ```bash
    docker run -p 8000:8000 -p 8501:8501 --env-file .env microbiology-farm
    ```
This will start the application, and you can access the Streamlit UI at `http://localhost:8501`.
