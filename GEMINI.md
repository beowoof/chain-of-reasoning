# Project Constitution & Coding Standards
**Version: 1.0**
**Date: 2025-08-02**

## 1. Core Philosophy

This document outlines the mandatory architectural and coding standards for this project. All generated code must adhere strictly to these principles. The goal is to produce a professional, robust, maintainable, and scalable Python application.

-   **Modularity & Separation of Concerns:** The application must be strictly divided into logical layers. Do not mix database logic, API business logic, and presentation code.
-   **Clarity & Robustness:** Code must be explicit, readable, and type-safe. The goal is clarity over terse cleverness.
-   **Modern Asynchronous Practices:** The application is built on an async-first framework (FastAPI). All I/O-bound operations must be asynchronous to prevent blocking the event loop.

## 2. Core Technology Stack

All code must be compatible with and utilise the following technologies. Do not suggest alternatives unless explicitly asked.

-   **Backend Framework:** FastAPI
-   **UI Framework:** Streamlit
-   **LLM Orchestration:** LangChain
-   **Data Validation & Settings:** Pydantic
-   **Static Type Checking:** `mypy` (in strict mode)
-   **Linting & Formatting:** `Ruff`

## 3. Strict Coding Standards

### a. Type Hinting (`mypy`)
All function and method signatures **must** include full type hints for arguments and return values. All variable declarations should be typed. The codebase will be validated using `mypy --strict`.

**BAD:**
```python
def process_data(data):
    name = data["name"]
    return f"Hello, {name}"
```

**GOOD:**
```python
from typing import Dict, Any

def process_data(data: Dict[str, Any]) -> str:
    name: str = data["name"]
    return f