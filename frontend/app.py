import streamlit as st
import requests, uuid

BACKEND_URL = "http://localhost:8001/chat"

st.set_page_config(
    page_title="Arpit AI Persona",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Arpit AI Persona")

st.markdown(
"""
Ask me about:

- Resume
- Experience
- Skills
- Education
- Certifications
- GitHub Projects
- ATS Analyzer
- Arxiv Scraper
- CourseCrafterAI

I answer only from Arpit's resume and repositories.
"""
)

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


prompt = st.chat_input(
    "Ask about Arpit..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())

        response = requests.post(
            BACKEND_URL,
            json={
                "session_id": st.session_state.session_id,
                "message": prompt
            },
            timeout=120
        )

        answer = response.json()["answer"]

    except Exception as e:

        answer = (
            "Unable to reach backend.\n\n"
            f"Error: {str(e)}"
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)