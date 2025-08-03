# Chain of Reasoning AI Assistant

This project implements a sophisticated AI assistant designed to answer user questions by leveraging both local document search and web search capabilities. It utilizes a "chain of reasoning" approach, breaking down complex queries and employing appropriate tools to gather information before formulating a concise answer.

## Features

*   **Intelligent Question Answering:** Answers user questions using a step-by-step reasoning process, showing its thought process and tool selection rationale.
*   **Local Document Search (RAG Fusion):** Efficiently searches and retrieves information from a local vector store using FAISS, with automatic document chunking and overlap for improved context preservation.
*   **Web Search Integration:** Utilizes Tavily API for real-time web search, with smart summarization of results to maintain relevance and conciseness.
*   **PDF and URL Ingestion:** Allows users to upload PDF documents and provide URLs, automatically processing them into searchable chunks with configurable overlap.
*   **Modular Backend (FastAPI):** A robust backend with async support, proper error handling, and a well-structured agent system using LangChain.
*   **Interactive Frontend (Streamlit):** A user-friendly web interface with progress indicators, error handling, and clear feedback for all operations.

## Technology Stack

This project is built with the following core technologies:

*   **Backend Framework:** FastAPI
*   **UI Framework:** Streamlit
*   **LLM Orchestration:** LangChain
*   **Data Validation & Settings:** Pydantic
*   **Static Type Checking:** `mypy` (in strict mode)
*   **Linting & Formatting:** `ruff`

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

5.  **Download Ollama and required models:**
    This project uses Ollama to run two models locally:
    *   Download and install Ollama from [ollama.com](https://ollama.com/)
    *   Pull the required models:
        ```bash
        # Main reasoning model
        ollama pull llama3:instruct
        # Embeddings model for document search
        ollama pull mxbai-embed-large:latest
        ```
    
6.  **Create required directories:**
    ```bash
    mkdir -p data/faiss_index
    ```

## Running the Application

### On Unix/Linux/MacOS
Execute the `start.sh` script:

```bash
./start.sh
```

### On Windows
Execute the `start.ps1` script in PowerShell:
```powershell
.\start.ps1
```

Both scripts will:
1.  Check if Ollama is running and start it if needed
2.  Verify required models are downloaded
3.  Start the FastAPI backend
4.  Start the Streamlit frontend

You can then access the Streamlit application in your browser at `http://localhost:8501` (or the address provided in your terminal).

### Additional Windows Setup Notes
If you encounter build errors during `poetry install`, follow these steps:

1. Install Visual C++ build tools:
   - Download "Build Tools for Visual Studio 2022" from the [Microsoft Visual Studio website](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - During installation, select "Desktop development with C++"

2. Ensure you have Python 3.13 installed:
   - Download from [Python.org](https://www.python.org/downloads/)
   - Add Python to PATH during installation

3. Set up the environment:
```powershell
poetry env use python3.13
poetry install
```

## Project Structure

```
.
├── .git/
├── .gitignore
├── .env                # Environment variables (you need to create this)
├── GEMINI.md
├── pyproject.toml
├── README.md
├── start.sh           # Unix/Linux/MacOS startup script
├── start.ps1          # Windows PowerShell startup script
├── data/
│   └── faiss_index/   # Local vector store for documents
├── tests/             # Unit and integration tests
│   ├── test_agent.py  # Agent-specific tests
│   └── test_main.py   # API and integration tests
└── src/
    ├── backend/
    │   ├── main.py          # FastAPI backend with LangChain agent
    │   ├── agent.py         # Agent implementation with BaseTool
    │   ├── vector_store.py  # Vector store and document processing
    │   └── __pycache__/
    └── frontend/
        └── app.py           # Streamlit user interface
```

## Contributing

Contributions are welcome! Please ensure your code adheres to the coding standards outlined in `GEMINI.md`.
