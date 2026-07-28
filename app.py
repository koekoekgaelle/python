import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from assistant.chatbot import create_chatbot, create_new_conversation
from assistant.document_loader import load_pdf
from assistant.chunker import create_chunks
from assistant.vectordb import create_vectorstore

# =========================
# Configuratie
# =========================

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY ontbreekt in het .env-bestand.")
    st.stop()

st.set_page_config(
    page_title="Mijn AI-assistent",
    page_icon="🤖",
)

st.title("🤖 Mijn AI-assistent")

# =========================
# Sidebar
# =========================

with st.sidebar:
    st.header("🤖 Mijn AI-assistent")

    if st.button("🗑️ Nieuw gesprek"):
        st.session_state.gesprek = create_new_conversation()
        st.rerun()

    st.divider()

    uploaded_file = st.file_uploader(
        "📄 Upload een PDF",
        type=["pdf"]
    )

    st.divider()

    if "gesprek" in st.session_state:
        aantal = len(st.session_state.gesprek) - 1
    else:
        aantal = 0

    st.write(f"💬 Berichten: {max(aantal, 0)}")

# =========================
# PDF verwerken
# =========================

if uploaded_file is not None:
   text = load_pdf(uploaded_file)
   chunks = create_chunks(text)

   vectorstore = create_vectorstore(chunks)

   st.success(f"✅ {uploaded_file.name} geladen!")

   st.info(f"📦 {len(chunks)} chunks gemaakt.")

   st.success("🗄️ Vector database aangemaakt!")

# =========================
# Chat initialiseren
# =========================

if "gesprek" not in st.session_state:
    st.session_state.gesprek = create_new_conversation()

chatbot = create_chatbot()

# =========================
# Chatgeschiedenis tonen
# =========================

for bericht in st.session_state.gesprek:
    if isinstance(bericht, HumanMessage):
        with st.chat_message("user"):
            st.write(bericht.content)

    elif isinstance(bericht, AIMessage):
        with st.chat_message("assistant"):
            st.write(bericht.content)

# =========================
# Nieuw bericht
# =========================

vraag = st.chat_input("Typ hier je vraag")

if vraag:
    st.session_state.gesprek.append(
        HumanMessage(content=vraag)
    )

    with st.chat_message("user"):
        st.write(vraag)

    try:
        with st.chat_message("assistant"):
            volledig_antwoord = ""
            placeholder = st.empty()

            for stukje in chatbot.stream(st.session_state.gesprek):
                if stukje.content:
                    volledig_antwoord += stukje.content
                    placeholder.markdown(volledig_antwoord + "▌")

            placeholder.markdown(volledig_antwoord)

        st.session_state.gesprek.append(
            AIMessage(content=volledig_antwoord)
        )

    except Exception as fout:
        st.error(f"Er ging iets mis: {fout}")