# Chain of Reasoning AI Assistant

This project implements a sophisticated AI assistant designed to answer user questions by leveraging both local document search and web search capabilities. It utilizes a "chain of reasoning" approach, breaking down complex queries and employing appropriate tools to gather information before formulating a concise answer.

## Features

*   **Intelligent Question Answering:** Answers user questions by reasoning through the problem and selecting the best information source.
*   **Local Document Search (RAG Fusion):** Efficiently searches and retrieves information from a local vector store, enhanced with a RAG (Retrieval-Augmented Generation) Fusion technique for improved relevance.
*   **Web Search Integration:** Utilizes Tavily API for real-time web search to answer questions requiring current events or general knowledge.
*   **PDF and URL Ingestion:** Allows users to upload PDF documents and provide URLs to expand the local knowledge base.
*   **Modular Backend (FastAPI):** A robust and scalable backend built with FastAPI.
*   **Interactive Frontend (Streamlit):** A user-friendly web interface for interacting with the AI assistant.

## Technology Stack

This project is built with the following core technologies:

*   **Backend Framework:** FastAPI
*   **UI Framework:** Streamlit
*   **LLM Orchestration:** LangChain
*   **Data Validation & Settings:** Pydantic
*   **Static Type Checking:** `mypy` (in strict mode)
*   **Linting & Formatting:** `Ruff`

## Setup and Installation

To set up the project, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/chain-of-reasoning.git
    cd chain-of-reasoning
    ```

2.  **Install Poetry (if you don't have it):**
    ```bash
    pip install poetry
    ```

3.  **Install dependencies:**
    ```bash
    poetry install
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the project root and add your Tavily API key:
    ```
    TAVILY_API_KEY="your_tavily_api_key_here"
    ```
    You can obtain a Tavily API key from [Tavily AI](https://tavily.com/).

5.  **Download Ollama and the Llama3 model:**
    This project uses Ollama to run the `llama3:instruct` model locally.
    *   Download and install Ollama from [ollama.com](https://ollama.com/).
    *   Pull the `llama3:instruct` model:
        ```bash
        ollama pull llama3:instruct
        ```

## Running the Application

To run the application, execute the `start.sh` script:

```bash
./start.sh
```

This script will:
1.  Start the FastAPI backend.
2.  Start the Streamlit frontend.

You can then access the Streamlit application in your browser at `http://localhost:8501` (or the address provided in your terminal).

## Project Structure

```
.
├── .git/
├── .gitignore
├── GEMINI.md
├── pyproject.toml
├── README.md
├── start.sh
├── data/
│   └── faiss_index/  # Local vector store for documents
└── src/
    ├── backend/
    │   ├── main.py          # FastAPI application entry point
    │   ├── vector_store.py  # Logic for vector store operations
    │   └── __pycache__/
    └── frontend/
        └── app.py           # Streamlit application entry point
```

## Contributing

Contributions are welcome! Please ensure your code adheres to the coding standards outlined in `GEMINI.md`.
