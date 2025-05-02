import streamlit as st
import requests
import os

st.set_page_config(page_title="Custom AI Bot", layout="centered")
st.title("🧠 Build Your Custom AI Bot")

# Optional: use environment variable for backend
API_URL = os.getenv("API_URL", "https://propertyagent.onrender.com/chat")

# Config inputs
st.subheader("🔧 MongoDB Connection")
mongo_uri = st.text_input("Mongo URI")
mongo_db = st.text_input("Mongo DB Name")
mongo_collections = st.text_input("Collections (comma-separated)")

# File upload
st.subheader("📁 Upload a document")
uploaded_file = st.file_uploader("Choose file", type=["pdf", "txt", "docx"])

# Query box
st.subheader("💬 Ask your data")
query = st.text_input("Your question")

if st.button("Ask"):
    if not query:
        st.warning("❗ Please enter a question.")
    elif not mongo_uri and not uploaded_file:
        st.warning("❗ Please provide at least a Mongo URI or upload a document.")
    else:
        with st.spinner("🤖 Thinking..."):
            files = {"file": uploaded_file} if uploaded_file else None
            payload = {
                "message": query,
                "mongo_uri": mongo_uri,
                "mongo_db": mongo_db,
                "mongo_collections": mongo_collections
            }

            try:
                response = requests.post(API_URL, data=payload, files=files)
                response.raise_for_status()
                answer = response.json()["response"]
                st.success("✅ Answer:")
                st.write(answer)
            except Exception as e:
                st.error(f"❌ API Error: {e}")
