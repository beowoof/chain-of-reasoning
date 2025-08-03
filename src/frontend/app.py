import streamlit as st
import httpx

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"
# Set a longer timeout for potentially slow operations
CLIENT_TIMEOUT = 300.0  # 5 minutes

st.title("RAG Proof of Concept")

# --- Initialize Session State ---
if "last_uploaded_filename" not in st.session_state:
    st.session_state.last_uploaded_filename = None

# --- Reusable HTTP Client ---
client = httpx.Client(base_url=BACKEND_URL, timeout=CLIENT_TIMEOUT)

# --- Data Ingestion ---
st.header("1. Ingest Data")

# PDF Upload
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
if uploaded_file is not None and uploaded_file.name != st.session_state.last_uploaded_filename:
    with st.spinner("Processing PDF..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = client.post("/upload/pdf", files=files)
            response.raise_for_status()
            st.session_state.last_uploaded_filename = uploaded_file.name
            st.success(response.json()["message"])
        except httpx.RequestError as e:
            st.error(f"Error connecting to backend: {e}")
        except httpx.HTTPStatusError as e:
            st.error(f"Error from backend: {e.response.status_code} - {e.response.text}")

# URL Upload
url = st.text_input("Or enter a URL to scrape")
if st.button("Scrape URL"):
    if url:
        with st.spinner("Scraping URL..."):
            try:
                response = client.post("/upload/url", data={"url": url})
                response.raise_for_status()
                st.success(response.json()["message"])
            except httpx.RequestError as e:
                st.error(f"Error connecting to backend: {e}")
            except httpx.HTTPStatusError as e:
                st.error(f"Error from backend: {e.response.status_code} - {e.response.text}")
    else:
        st.warning("Please enter a URL.")

# --- Q&A ---
st.header("2. Ask a Question")
question = st.text_input("Ask a question about your documents:")

if st.button("Submit"):
    if question:
        with st.spinner("Thinking..."):
            try:
                response = client.post("/ask", json={"text": question})
                response.raise_for_status()
                response_data = response.json()
                
                # Display the answer
                st.write("**Answer:**")
                st.write(response_data["answer"])
                
                # Display thinking steps in a collapsible section
                if "thinking_steps" in response_data:
                    with st.expander("Show thinking process"):
                        for step in response_data["thinking_steps"]:
                            st.markdown("---")
                            st.markdown(f"**Action:** {step['action']}")
                            st.markdown(f"**Input:** {step['input']}")
                            st.markdown(f"**Observation:** {step['observation']}")
            except httpx.RequestError as e:
                st.error(f"Error connecting to backend: {e}")
            except httpx.HTTPStatusError as e:
                st.error(f"Error from backend: {e.response.status_code} - {e.response.text}")
    else:
        st.warning("Please enter a question.")
