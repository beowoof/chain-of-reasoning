import pytest
from unittest.mock import MagicMock, patch
from langchain_core.runnables import Runnable

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
    from src.backend import agent
    # Patch Ollama to avoid real model loading
    agent.Ollama = MockOllama
    with pytest.raises(ValueError):
        agent.create_agent()

def test_rag_fusion_retrieval_empty_docs(monkeypatch):
    """Test rag_fusion_retrieval returns message if no docs found."""
    from src.backend import agent
    monkeypatch.setenv("TAVILY_API_KEY", "dummy")
    mock_vector_store = MagicMock()
    mock_retriever = MagicMock()
    mock_retriever.invoke.return_value = []
    mock_vector_store.as_retriever.return_value = mock_retriever
    agent.Ollama = MockOllama
    tools = agent.create_agent(vector_store=mock_vector_store).tools
    tool = next(t for t in tools if t.name == "Local Document Search")
    assert tool.invoke("irrelevant query") == "No relevant information found in local documents."

def test_summarized_web_search_empty_results(monkeypatch):
    """Test summarized_web_search returns message if no web results found."""
    from src.backend import agent
    monkeypatch.setenv("TAVILY_API_KEY", "dummy")
    agent.Ollama = MockOllama
    mock_client = MagicMock()
    mock_client.search.return_value = {"results": []}
    with patch("src.backend.agent.TavilyClient", return_value=mock_client):
        tools = agent.create_agent().tools
        tool = next(t for t in tools if t.name == "Web Search")
        assert tool.invoke("irrelevant query") == "No results found on the web."

@patch("src.backend.agent.os.getenv", return_value="dummy_tavily_key")
@patch("src.backend.agent.Ollama")
@patch("src.backend.agent.TavilyClient")
def test_create_agent_initialization(mock_tavily_client, mock_ollama, mock_getenv):
    """Test if create_agent initializes correctly."""
    from src.backend import agent
    agent_executor = agent.create_agent()
    assert agent_executor is not None
    assert hasattr(agent_executor, "agent")
    assert hasattr(agent_executor, "tools")
    assert len(agent_executor.tools) == 2  # Local Document Search and Web Search
