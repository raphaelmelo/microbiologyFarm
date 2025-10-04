#!/bin/bash
# run.sh

# Start the FastAPI backend, using the PORT environment variable provided by Cloud Run
# The default to 8000 is for local development.
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} &

# The Streamlit frontend will not be exposed on Cloud Run in this configuration,
# as a service can only expose one port.
# To run Streamlit on Cloud Run, it would need to be a separate service.
# streamlit run app.py --server.port 8501 --server.address 0.0.0.0
