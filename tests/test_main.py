import pytest
from unittest.mock import MagicMock, patch
from src.backend.main import app, create_agent, Question
from fastapi.testclient import TestClient

# Initialize TestClient for FastAPI application
client = TestClient(app)

from langchain_core.runnables import Runnable  # noqa: F401
class MockOllama(Runnable):
    def __init__(self, *args, **kwargs):
        pass
    def invoke(self, *args, **kwargs):
        return ""
    def bind(self, *args, **kwargs):
        return self

def test_create_agent_missing_env(monkeypatch):
    """Test create_agent raises error if TAVILY_API_KEY is missing."""
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    from src.backend import main
    # Patch Ollama to avoid real model loading
    main.Ollama = MockOllama
    with pytest.raises(ValueError):
        main.create_agent()

def test_rag_fusion_retrieval_empty_docs(monkeypatch):
    """Test rag_fusion_retrieval returns message if no docs found."""
    from src.backend import main
    monkeypatch.setenv("TAVILY_API_KEY", "dummy")
    main.vector_store = MagicMock()
    main.vector_store.as_retriever.return_value.invoke.return_value = []
    main.Ollama = MockOllama
    agent = main.create_agent()
    tool = next(t for t in agent.tools if t.name == "Local Document Search")
    assert tool("irrelevant query") == "No relevant information found in local documents."

def test_summarized_web_search_empty_results(monkeypatch):
    """Test summarized_web_search returns message if no web results found."""
    from src.backend import main
    monkeypatch.setenv("TAVILY_API_KEY", "dummy")
    main.Ollama = MockOllama
    main.TavilyClient = MagicMock()
    main.TavilyClient.return_value.search.return_value = {"results": []}
    agent = main.create_agent()
    tool = next(t for t in agent.tools if t.name == "Web Search")
    assert tool("irrelevant query") == "No results found on the web."


@patch("src.backend.main.os.getenv", return_value="dummy_tavily_key")
@patch("src.backend.main.Ollama")
@patch("src.backend.main.TavilyClient")
def test_create_agent_initialization(mock_tavily_client, mock_ollama, mock_getenv):
    """Test if create_agent initializes correctly."""
    agent_executor = create_agent()
    assert agent_executor is not None
    assert hasattr(agent_executor, "agent")
    assert hasattr(agent_executor, "tools")
    assert len(agent_executor.tools) == 2 # Local Document Search and Web Search

def test_ask_endpoint_no_agent():
    """Test /ask endpoint when agent is not initialized."""
    with patch("src.backend.main.agent_executor", None):
        response = client.post("/ask", json={"text": "What is AI?"})
        assert response.status_code == 200
        assert response.json() == {"error": "Agent not initialized."} 

@patch("src.backend.main.agent_executor")
def test_ask_endpoint_success(mock_agent_executor):
    """Test /ask endpoint with a successful agent invocation."""
    mock_agent_executor.invoke.return_value = {"output": "The answer is 42.", "intermediate_steps": []}
    response = client.post("/ask", json={"text": "What is the meaning of life?"})
    assert response.status_code == 200
    assert response.json() == {"answer": "The answer is 42."}
    mock_agent_executor.invoke.assert_called_once_with({"input": "What is the meaning of life?"})

@patch("src.backend.main.agent_executor")
def test_ask_endpoint_exception(mock_agent_executor):
    """Test /ask endpoint when agent invocation raises an exception."""
    mock_agent_executor.invoke.side_effect = Exception("Agent error")
    response = client.post("/ask", json={"text": "Cause an error"})
    assert response.status_code == 200
    assert "An error occurred: Agent error" in response.json()["error"]

@patch("src.backend.main.load_documents_from_pdf", side_effect=Exception("PDF load error"))
@patch("src.backend.main.process_and_store_documents")
@patch("src.backend.main.create_agent")
def test_upload_pdf_endpoint_error(mock_create_agent, mock_process_and_store_documents, mock_load_documents_from_pdf, tmp_path):
    """Test /upload/pdf endpoint with PDF load error."""
    pdf_path = tmp_path / "dummy.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"dummy pdf content")
    with open(pdf_path, "rb") as f:
        response = client.post("/upload/pdf", files={"file": ("dummy.pdf", f, "application/pdf")})
    assert response.status_code == 500 or response.status_code == 200
    # Should return error or handle gracefully
    mock_load_documents_from_pdf.assert_called_once_with(str(pdf_path))

@patch("src.backend.main.load_documents_from_url")
@patch("src.backend.main.process_and_store_documents")
@patch("src.backend.main.create_agent")
def test_upload_url_endpoint(mock_create_agent, mock_process_and_store_documents, mock_load_documents_from_url):
    """Test /upload/url endpoint."""
    mock_load_documents_from_url.return_value = [MagicMock()]
    mock_process_and_store_documents.return_value = MagicMock()
    mock_create_agent.return_value = MagicMock()

    response = client.post("/upload/url", data={"url": "http://example.com"})
    
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully scraped and processed http://example.com"}
    mock_load_documents_from_url.assert_called_once_with("http://example.com")
    mock_process_and_store_documents.assert_called_once()
    mock_create_agent.assert_called_once()
