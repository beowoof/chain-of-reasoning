from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
import os
from .vector_store import (
    get_embeddings,
    load_vector_store,
    process_and_store_documents,
    load_documents_from_pdf,
    load_documents_from_url,
)
from .agent import create_agent, summarise_answer

# --- Global State ---
vector_store = None
embeddings = None
agent_executor = None

@asynccontextmanager
async def lifespan(app):
    global vector_store, embeddings, agent_executor
    print("Starting up and initializing resources...")
    embeddings = get_embeddings()
    vector_store = load_vector_store(embeddings)
    try:
        agent_executor = create_new_agent()
    except ValueError as e:
        # Gracefully handle missing configuration such as API keys.
        print(f"Agent initialisation failed: {e}")
        agent_executor = None
    print("Startup complete.")
    yield

app = FastAPI(lifespan=lifespan)

class Question(BaseModel):
    text: str

def create_new_agent():
    """
    Creates and configures a new agent instance using the current vector store.
    """
    return create_agent(vector_store)

# --- FastAPI Endpoints ---

@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_store, embeddings, agent_executor
    file_path = f"./{file.filename}"
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        new_docs = load_documents_from_pdf(file_path)
        vector_store = process_and_store_documents(new_docs, vector_store, embeddings)
        agent_executor = create_new_agent()
        return {"message": f"Successfully uploaded and processed {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/upload/url")
async def upload_url(url: str = Form(...)):
    global vector_store, embeddings, agent_executor
    new_docs = load_documents_from_url(url)
    vector_store = process_and_store_documents(new_docs, vector_store, embeddings)
    agent_executor = create_new_agent()
    return {"message": f"Successfully scraped and processed {url}"}

@app.post("/ask")
def ask(question: Question):
    if agent_executor is None:
        return {"error": "Agent not initialized."}

    try:
        response = agent_executor.invoke({"input": question.text})
        # Handle the new response format with intermediate steps.
        intermediate_steps = response.get("intermediate_steps", [])
        final_answer = response.get("output", "No final answer was generated.")
        
        # Format the thinking steps for the UI
        thinking_steps = []
        for step in intermediate_steps:
            thinking_steps.append({
                "action": step[0].tool,
                "input": step[0].tool_input,
                "observation": step[1]
            })
        
        improved_answer = summarise_answer(thinking_steps, final_answer)
        return {
            "answer": improved_answer,
            "thinking_steps": thinking_steps
        }
    except Exception as e:
        print(f"An error occurred during agent invocation: {e}")
        return {"error": "An internal error has occurred."}
