from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.tools import Tool
from tavily import TavilyClient
import os
import time
from .vector_store import (
    get_embeddings,
    load_vector_store,
    process_and_store_documents,
    load_documents_from_pdf,
    load_documents_from_url,
)
from langchain_core.output_parsers import StrOutputParser

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
    agent_executor = create_agent()
    print("Startup complete.")
    yield

app = FastAPI(lifespan=lifespan)

class Question(BaseModel):
    text: str

def create_agent():
    """
    Creates and configures the LangChain agent with tools, LLM, and a hardened prompt.
    This is the core logic for the agent's reasoning process.
    """
    print("Creating a new agent instance...")
    
    # --- LLM Configuration ---
    # The main reasoning LLM for the agent.
    llm = Ollama(model="llama3:instruct")

    # Create a separate, simpler LLM for summarization tasks.
    # This prevents the main agent from getting overwhelmed by long tool outputs.
    summarizer_llm = Ollama(model="llama3:instruct", temperature=0.0)
    
    # --- Tool Functions ---

    def rag_fusion_retrieval(query: str) -> str:
        """Performs a RAG search on local documents and returns a clean summary."""
        if vector_store is None:
            return "Vector store is not initialized. Cannot search local documents."

        print(f"Performing RAG search for: {query}")
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(query)

        if not docs:
            return "No relevant information found in local documents."

        # Instead of returning raw text, summarize it.
        context_text = "\n\n---\n\n".join([doc.page_content for doc in docs])
        prompt_template = ChatPromptTemplate.from_template(
            "Summarize the following text to answer the query '{query}'. "
            "Focus only on information directly relevant to the query.\n\n"
            "Text:\n{context}"
        )
        summarization_chain = prompt_template | summarizer_llm | StrOutputParser()
        return summarization_chain.invoke({"context": context_text, "query": query})

    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY environment variable not set.")
    tavily_client = TavilyClient(api_key=tavily_api_key)

    def summarized_web_search(query: str) -> str:
        """
        Performs a web search and then uses an LLM to summarize the results.
        This provides a clean, concise observation for the main agent.
        """
        print(f"Searching and summarizing the web for: {query}")
        time.sleep(1)
        try:
            response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
            results = response.get("results", [])
            if not results:
                return "No results found on the web."

            # Consolidate content for summarization
            context_text = "\n\n---\n\n".join([f"Source URL: {res['url']}\nContent: {res['content']}" for res in results])
            
            # Use the summarizer LLM
            prompt_template = ChatPromptTemplate.from_template(
                "You are an expert research assistant. Summarize the following text from a web search to concisely answer the user's query: '{query}'. "
                "Synthesize the information from all sources into a single, coherent paragraph. Cite the source URLs if relevant.\n\n"
                "Search Results:\n{context}"
            )
            summarization_chain = prompt_template | summarizer_llm | StrOutputParser()
            return summarization_chain.invoke({"context": context_text, "query": query})
        except Exception as e:
            return f"Error during web search and summarization: {e}"

    # --- Tools ---
    tools = [
        Tool(
            name="Local Document Search",
            func=rag_fusion_retrieval,
            description="Use this tool FIRST to search for information in local, user-provided documents. Input should be a clear and concise query.",
        ),
        Tool(
            name="Web Search",
            func=summarized_web_search,
            description="Use this tool to search the public internet for current events or general knowledge ONLY if local documents are insufficient.",
        )
    ]

    # --- Hardened Prompt ---
    # UPDATED: Added a more explicit rule to force the agent to conclude
    # as soon as it has a sufficient answer, preventing redundant steps.
    template = """
You are a reasoning engine. Your purpose is to use tools to find an answer.

You have access to the following tools:
{tools}

You MUST follow these rules strictly:
1. ALWAYS use "Local Document Search" first.
2. After EACH tool use, you MUST analyze the 'Observation'. If it contains a sufficient answer, you MUST immediately use the 'Final Answer' format. Do not use another tool if the answer has been found.
3. If the local search is not enough, and only then, use "Web Search".
4. You MUST use the following format. DO NOT add any other text.

Thought: Your one-sentence reason for using a tool or for concluding the search.
Action: The tool to use. Must be one of: [{tool_names}]
Action Input: The input for the tool.
Observation: [The tool's result will be here]

...this cycle can repeat...

When you have the answer, use this final format:
Thought: I have the final answer based on the previous observation.
Final Answer: The final answer.

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""
    prompt = PromptTemplate.from_template(template)

    # --- Agent ---
    agent = create_react_agent(llm, tools, prompt)
    
    # Added `return_intermediate_steps` for better debugging.
    return AgentExecutor(
        agent=agent, # type: ignore
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        return_intermediate_steps=True # This is key for debugging
    )

# --- FastAPI Endpoints ---

@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_store, embeddings, agent_executor
    file_path = f"./{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    new_docs = load_documents_from_pdf(file_path)
    vector_store = process_and_store_documents(new_docs, vector_store, embeddings)
    agent_executor = create_agent()
    os.remove(file_path)
    return {"message": f"Successfully uploaded and processed {file.filename}"}

@app.post("/upload/url")
async def upload_url(url: str = Form(...)):
    global vector_store, embeddings, agent_executor
    new_docs = load_documents_from_url(url)
    vector_store = process_and_store_documents(new_docs, vector_store, embeddings)
    agent_executor = create_agent()
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
        
        # You can now log or process the intermediate steps for debugging
        print("\n--- INTERMEDIATE STEPS ---")
        for step in intermediate_steps:
            print(f"Action: {step[0].tool}")
            print(f"Input: {step[0].tool_input}")
            print(f"Observation: {step[1]}")
            print("-" * 20)

        return {"answer": final_answer}
    except Exception as e:
        print(f"An error occurred during agent invocation: {e}")
        return {"error": f"An internal error occurred"}
