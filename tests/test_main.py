from unittest.mock import MagicMock, patch
from src.backend.main import app, Question
from fastapi.testclient import TestClient

# Initialize TestClient for FastAPI application
client = TestClient(app)

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
    assert response.json() == {
        "answer": "The answer is 42.",
        "thinking_steps": []
    }
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
    assert response.status_code == 400
    assert response.json()["detail"] == "PDF load error"
    mock_load_documents_from_pdf.assert_called_once()

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
