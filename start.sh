#!/bin/bash

# Exit on any error
set -e

# --- 1. Check and Start Ollama ---
echo "Checking if Ollama service is available..."
# Try to list models. If it fails, the service is likely down.
if ! ollama list > /dev/null 2>&1; then
    echo "Ollama service not responding. Starting it in the background..."
    ollama serve &
    OLLAMA_PID=$!
    echo "Waiting for Ollama to initialize..."
    # Wait until the service is responsive using an 'until' loop
    until ollama list > /dev/null 2>&1; do
        sleep 1
        echo -n "."
    done
    echo -e "\nOllama is ready."
else
    echo "Ollama is running."
fi

# --- 2. Check for Ollama Models ---
echo "Checking for required Ollama models..."

# Check for llama3:instruct
if ! ollama list | grep -q "llama3:instruct"; then
    echo "'llama3:instruct' model not found. Pulling it now..."
    ollama pull llama3:instruct
else
    echo "'llama3:instruct' model found."
fi

# Check for mxbai-embed-large:latest
if ! ollama list | grep -q "mxbai-embed-large:latest"; then
    echo "'mxbai-embed-large:latest' model not found. Pulling it now..."
    ollama pull mxbai-embed-large:latest
else
    echo "'mxbai-embed-large:latest' model found."
fi

# --- 3. Kill Existing Backend Process (if any) ---
echo "Checking for existing process on port 8000..."
if lsof -i :8000 -t > /dev/null; then
    echo "Process found on port 8000. Terminating it..."
    lsof -i :8000 -t | xargs kill -9
    sleep 1 # Give it a moment to release the port
else
    echo "No process found on port 8000."
fi

# --- 4. Set Environment Variables ---
echo "Setting environment variables..."
# Ensure the environment variable for Tavily API key is set
if [ -z "$TAVILY_API_KEY" ]; then
    echo "TAVILY_API_KEY is not set. Please set it before running this script."
    exit 1
fi

# --- 4. Start FastAPI Backend ---
echo "Starting FastAPI backend in the background..."
# Run from the project root so Python can find the package 'src'
poetry run uvicorn src.backend.main:app --reload &
BACKEND_PID=$!

# --- 5. Wait for Backend to be Ready ---
echo "Waiting for backend to be ready..."
while ! nc -z 127.0.0.1 8000; do
    sleep 0.5 # wait for 1/2 a second before check again
    echo -n "."
done
echo -e "\nBackend is ready!"

# --- 6. Start Streamlit Frontend ---
echo "Starting Streamlit frontend..."
# Run from the project root
poetry run streamlit run src/frontend/app.py

# --- Cleanup ---
# When the streamlit process is killed (e.g., with Ctrl+C),
# this part of the script will run.
echo -e "\nShutting down backend server..."
kill $BACKEND_PID

# If we started Ollama, shut it down too
if [ ! -z "$OLLAMA_PID" ]; then
    echo "Shutting down Ollama server..."
    kill $OLLAMA_PID
fi