import streamlit as st
import requests
import os

os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"

API_BASE = st.secrets.get("API_BASE")

if not API_BASE:
    st.error("🚨 API endpoint not set. Please configure the `API_BASE` in Streamlit secrets.")
    st.stop()
    
st.set_page_config(page_title="Document QA System", layout="centered")
st.title("📄 Document QA System")

# Session state to store uploaded filename
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False
if "filename" not in st.session_state:
    st.session_state.filename = None

# Upload section
st.header("1. Upload a document")
uploaded_file = st.file_uploader("Upload (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_file and st.button("Upload Document"):
    with st.spinner("Processing document..."):
        response = requests.post(
            f"{API_URL}/upload",
            files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        )
        if response.status_code == 200:
            st.success("Document uploaded and processed.")
            st.session_state.uploaded = True
            st.session_state.filename = response.json()["file"]
        else:
            st.error("Upload failed, try again later.")

# Question section
st.header("2. Ask a question")

if not st.session_state.uploaded:
    st.info("Please upload a document first.")
else:
    question = st.text_input("Type your question:")

    if st.button("Ask"):
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{API_URL}/ask",
                data={
                    "question": question,
                    "filename": st.session_state.filename
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data["answer"] == "No text found":
                    st.warning("No relevant text found in the document.")

                elif data["answer"] == "No answer found":
                    st.warning("Relevant text found, but no confident answer.")
                    with st.expander("📄 Relevant Text Chunk"):
                        st.write(data["chunk"])

                else:
                    st.success(f"✅ Answer: {data['answer']}")
                    st.write(f"**Confidence:** {data['confidence']}%")
                    st.write(f"**Similarity Score:** {data['score']}")
                    with st.expander("📄 Relevant Text Chunk"):
                        st.write(data["chunk"])
            else:
                st.error("Failed to get an answer. try again later.")
