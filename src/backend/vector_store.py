from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

# --- Constants ---
EMBEDDING_MODEL_NAME = "mxbai-embed-large:latest"
VECTOR_STORE_PATH = "data/faiss_index"

# --- Embedding Function ---
def get_embeddings():
    """Initializes the embedding model."""
    return OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)

# --- Vector Store Management ---
def load_vector_store(embeddings):
    """Loads the vector store from disk if it exists."""
    if os.path.exists(VECTOR_STORE_PATH):
        print(f"Loading vector store from {VECTOR_STORE_PATH}")
        # This is required to load a FAISS index created with a different langchain version
        # or when using pickle, which is the default.
        # It's a security risk if the file is from an untrusted source.
        return FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    return None

def process_and_store_documents(documents, vector_store, embeddings):
    """
    Splits documents, adds them to the vector store (creating it if necessary),
    and saves the store to disk.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    if vector_store is None:
        print("Creating new vector store.")
        vector_store = FAISS.from_documents(documents=splits, embedding=embeddings)
    else:
        print("Adding new documents to existing vector store.")
        vector_store.add_documents(splits)

    print(f"Saving vector store to {VECTOR_STORE_PATH}")
    vector_store.save_local(VECTOR_STORE_PATH)
    return vector_store

# --- Data Ingestion ---
def load_documents_from_pdf(pdf_path):
    """Loads documents from a PDF file."""
    loader = PyPDFLoader(pdf_path)
    return loader.load()

def load_documents_from_url(url):
    """Loads documents from a web page."""
    loader = WebBaseLoader(url)
    return loader.load()
