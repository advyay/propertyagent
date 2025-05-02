import streamlit as st
import requests
import os

# Page settings
st.set_page_config(page_title="Custom AI Bot", layout="centered")
st.title("🧠 Build Your Custom AI Bot")

# Backend endpoint
API_URL = os.getenv("API_URL", "https://propertyagent.onrender.com/chat")

# Setup session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# MongoDB inputs
st.subheader("🔧 MongoDB Connection")
mongo_uri = st.text_input("Mongo URI", placeholder="mongodb+srv://username:pass@cluster.mongodb.net/")
mongo_db = st.text_input("Mongo DB Name", placeholder="e.g. axproperty")
mongo_collections = st.text_input("Collections (comma-separated)", placeholder="bookings,leads,projects")

# File upload
st.subheader("📁 Upload a document")
uploaded_file = st.file_uploader("Choose file", type=["pdf", "txt", "docx"])

# Question box
st.subheader("💬 Ask your data")
query = st.text_input("Your question")

# Submit
if st.button("Ask"):
    if not query:
        st.warning("❗ Please enter a question.")
    elif not mongo_uri.strip() and not uploaded_file:
        st.warning("❗ Please provide either a Mongo URI or upload a document.")
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
                answer = response.json().get("response", "⚠️ No response returned.")

                # Store in chat history
                st.session_state.history.append(("You", query))
                st.session_state.history.append(("AI", answer))
            except requests.exceptions.HTTPError as http_err:
                error_msg = f"❌ HTTP Error: {http_err.response.status_code} - {http_err.response.text}"
                st.session_state.history.append(("AI", error_msg))
            except Exception as e:
                st.session_state.history.append(("AI", f"❌ API Error: {e}"))

# Chat display
if st.session_state.history:
    st.subheader("📜 Chat History")
    for role, text in reversed(st.session_state.history):  # newest on top
        with st.chat_message(role.lower()):
            st.markdown(text)
