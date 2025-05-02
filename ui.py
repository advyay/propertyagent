import streamlit as st
import requests

st.title("🧠 Build Your Custom AI Bot")

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
    # Upload file to backend
    files = {"file": uploaded_file} if uploaded_file else None
    payload = {
        "message": query,
        "mongo_uri": mongo_uri,
        "mongo_db": mongo_db,
        "mongo_collections": mongo_collections
    }
    response = requests.post("https://propertyagent.onrender.com/chat", data=payload, files=files)
    st.write("🤖", response.json()["response"])
