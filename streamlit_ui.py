import streamlit as st
import requests
import os

# Prevent inotify errors on Linux
os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"

# Load API base from Streamlit Secrets
API_BASE = st.secrets.get("API_BASE")

if not API_BASE:
    st.error("🚨 API endpoint not set. Please configure the `API_BASE` in Streamlit secrets.")
    st.stop()

st.set_page_config(page_title="Document QA System", layout="centered")
st.title("📄 Document QA System")

# Session state to track file upload
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

# 1. Upload Section
st.header("1. Upload a document")
uploaded_file = st.file_uploader("Upload a file (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_file and st.button("Upload Document"):
    with st.spinner("Uploading and processing document..."):
        try:
            response = requests.post(
                f"{API_BASE}/upload",
                files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
                timeout=60
            )
            if response.status_code == 200:
                st.success("✅ Document uploaded and processed.")
                st.session_state.uploaded = True
            else:
                st.error("❌ Upload failed. Please try again.")
        except Exception as e:
            st.error(f"❌ Upload error: {e}")
            st.stop()

# 2. Ask a Question
st.header("2. Ask a question")

if not st.session_state.uploaded:
    st.info("Please upload a document first.")
else:
    question = st.text_input("Type your question:")
    if st.button("Ask"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Searching for an answer..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/ask",
                        data={"question": question},
                        timeout=60
                    )

                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer")

                        if answer == "no text found":
                            st.warning("⚠️ No relevant text found in the document.")
                        elif answer == "no answer found":
                            st.warning("🤔 Relevant text found, but no confident answer.")
                            with st.expander("📄 Relevant Text Chunk"):
                                st.write(data.get("chunk", ""))
                        else:
                            st.success(f"✅ Answer: {answer}")
                            st.write(f"**Confidence:** {data['confidence']}%")
                            st.write(f"**Similarity Score:** {data['score']}")
                            with st.expander("📄 Relevant Text Chunk"):
                                st.write(data.get("chunk", ""))
                    else:
                        st.error("❌ Failed to get an answer. Please try again later.")
                except Exception as e:
                    st.error(f"❌ Request failed: {e}")
