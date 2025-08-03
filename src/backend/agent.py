"""
Agent configuration and creation module.
"""
from langchain_community.llms import Ollama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.tools import BaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores.faiss import FAISS
from tavily import TavilyClient
import os
import time

def create_rag_tool(vector_store: FAISS | None, summarizer_llm: Ollama) -> BaseTool:
    """Creates the RAG tool with vector store dependency."""
    class RagTool(BaseTool):
        name: str = "Local Document Search"
        description: str = "Use this tool FIRST to search for information in local, user-provided documents. Input should be a clear and concise query."

        def _run(self, query: str) -> str:
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
    
    return RagTool()

def create_web_search_tool(tavily_api_key: str | None, summarizer_llm: Ollama) -> BaseTool:
    """Creates the web search tool with Tavily API key dependency."""
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY environment variable not set.")
    
    tavily_client = TavilyClient(api_key=tavily_api_key)

    class WebSearchTool(BaseTool):
        name: str = "Web Search"
        description: str = "Use this tool to search the public internet for current events or general knowledge ONLY if local documents are insufficient."

        def _run(self, query: str) -> str:
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
    
    return WebSearchTool()

def create_agent(vector_store: FAISS | None = None) -> AgentExecutor:
    """
    Creates and configures the LangChain agent with tools, LLM, and a hardened prompt.
    This is the core logic for the agent's reasoning process.
    
    Args:
        vector_store: Optional FAISS vector store for document search
    
    Returns:
        An initialized AgentExecutor
    """
    print("Creating a new agent instance...")
    
    # --- LLM Configuration ---
    # The main reasoning LLM for the agent.
    llm = Ollama(model="llama3:instruct")

    # Create a separate, simpler LLM for summarization tasks.
    # This prevents the main agent from getting overwhelmed by long tool outputs.
    summarizer_llm = Ollama(model="llama3:instruct", temperature=0.0)
    
    # --- Tools ---
    tools = [
        create_rag_tool(vector_store, summarizer_llm),
        create_web_search_tool(os.getenv("TAVILY_API_KEY"), summarizer_llm)
    ]

    # --- Hardened Prompt ---
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
    
    return AgentExecutor(
        agent=agent, # type: ignore
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        return_intermediate_steps=True # This is key for debugging
    )
