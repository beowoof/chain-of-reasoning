# Copilot Instructions for Chain of Reasoning Project

## Project Overview
This is a Python-based AI assistant project using FastAPI, LangChain, and Streamlit. The project implements a sophisticated question-answering system with RAG (Retrieval-Augmented Generation) capabilities and web search integration.

## Code Structure Guidelines

### Backend Organization (`src/backend/`)
- Keep agent-related logic in `agent.py`
- Vector store operations belong in `vector_store.py`
- FastAPI routes and app configuration stay in `main.py`

### Type Hints and Documentation
- Use Python 3.13+ type hints consistently
- Document all functions with clear docstrings
- Specify return types for all functions
- Example:
```python
def create_agent(vector_store: FAISS | None = None) -> AgentExecutor:
    """
    Creates and configures the LangChain agent with tools.
    
    Args:
        vector_store: Optional FAISS vector store for document search
    
    Returns:
        An initialized AgentExecutor
    """
```

### Testing Guidelines (`tests/`)
- Write test cases for all new functionality
- Use pytest fixtures for common setup
- Mock external dependencies (Ollama, Tavily)
- Group tests by component (e.g., `test_agent.py`, `test_main.py`)
- Example test structure:
```python
@patch("src.backend.main.agent_executor")
def test_functionality_name(mock_dependency):
    """Test description."""
    # Arrange
    mock_dependency.configure()
    # Act
    result = function_under_test()
    # Assert
    assert expected == result
```

### LangChain Integration
- Use modern imports from langchain_core and langchain_community
- Implement tools using BaseTool from langchain.tools
- Follow the chain-of-thought prompting pattern
- Handle tool outputs with proper error handling

### Environment and Dependencies
- Use Poetry for dependency management
- Keep `pyproject.toml` updated with explicit versions
- Include all optional dependencies in groups
- Document environment variables in README.md

### API Design Practices
- Use Pydantic models for request/response validation
- Implement proper error handling with HTTPException
- Return structured responses with thinking steps
- Example response format:
```python
{
    "answer": str,
    "thinking_steps": List[Dict[str, str]]
}
```

### Frontend Development (Streamlit)
- Use session state for persistent data
- Implement proper error handling and user feedback
- Show processing indicators for long operations
- Structure UI with clear sections and headers

## Common Patterns

### Agent Tool Creation
```python
class CustomTool(BaseTool):
    name: str = "Tool Name"
    description: str = "Clear description of when to use this tool"

    def _run(self, query: str) -> str:
        # Implementation
        return result
```

### Error Handling
```python
try:
    result = operation()
except SpecificException as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    print(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Vector Store Operations
```python
def process_documents(docs: List[Document], store: FAISS | None) -> FAISS:
    """Process and store documents in vector store."""
    if store is None:
        store = FAISS.from_documents(docs, embeddings)
    else:
        store.add_documents(docs)
    return store
```

## Project-Specific Conventions

### File Naming
- Test files: `test_*.py`
- Backend modules: Descriptive, single-purpose names
- Frontend components: `app.py` for main UI

### Documentation
- Keep README.md updated with new features
- Document environment setup steps
- Include examples for new functionality
- Explain any non-obvious design decisions

### Code Quality
- Run pytest before committing
- Ensure type hints are complete
- Follow PEP 8 style guidelines
- Use meaningful variable names

### Security Practices
- Never commit API keys or secrets
- Use environment variables for configuration
- Validate all user inputs
- Handle file uploads securely

## Best Practices for Contributions

1. **Before Starting**
   - Ensure all tests pass
   - Check for existing related issues
   - Update dependencies if needed

2. **During Development**
   - Write tests first (TDD approach)
   - Keep commits focused and atomic
   - Document new functions and classes
   - Update README if adding features

3. **Before Committing**
   - Run full test suite
   - Check type hints with mypy
   - Format code with ruff
   - Update documentation

4. **Deployment Considerations**
   - Verify environment variables
   - Test with clean environment
   - Check Ollama model availability
   - Validate API endpoints
