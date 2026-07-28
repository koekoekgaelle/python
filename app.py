import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from assistant.chatbot import create_chatbot, create_new_conversation
from assistant.document_loader import load_pdf
from assistant.chunker import create_chunks
from assistant.vectordb import create_vectorstore
from assistant.retriever import search_documents

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
    document_id = f"{uploaded_file.name}-{uploaded_file.size}"

    # Alleen verwerken wanneer er een nieuw bestand is geüpload
    if st.session_state.get("document_id") != document_id:
        text = load_pdf(uploaded_file)
        chunks = create_chunks(text)

        vectorstore = create_vectorstore(chunks)

        st.session_state.vectorstore = vectorstore
        st.session_state.document_id = document_id
        st.session_state.document_name = uploaded_file.name
        st.session_state.aantal_chunks = len(chunks)

    st.success(
        f"✅ {st.session_state.document_name} geladen!"
    )

    st.info(
        f"📦 {st.session_state.aantal_chunks} chunks beschikbaar."
    )

    st.success("🗄️ Vector database gereed!")
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
        # =========================
        # Bepalen welke berichten GPT krijgt
        # =========================

        if "vectorstore" in st.session_state:
            # PDF is aanwezig: gebruik retrieval
            results = search_documents(
                st.session_state.vectorstore,
                vraag,
                k=3,
            )

            context = "\n\n---\n\n".join(
                doc.page_content for doc in results
            )

            rag_vraag = HumanMessage(
                content=f"""
Gebruik de onderstaande documentcontext om de vraag te beantwoorden.

Als het antwoord niet in de context staat, zeg dan eerlijk dat je
het niet in het geüploade document kunt vinden.

CONTEXT:
{context}

VRAAG:
{vraag}
"""
            )

            berichten_voor_model = (
                st.session_state.gesprek[:-1]
                + [rag_vraag]
            )

        else:
            # Geen PDF aanwezig: gewone chatbot
            results = []
            berichten_voor_model = st.session_state.gesprek

        # =========================
        # Antwoord genereren
        # =========================

        with st.chat_message("assistant"):
            volledig_antwoord = ""
            placeholder = st.empty()

            for stukje in chatbot.stream(berichten_voor_model):
                if stukje.content:
                    volledig_antwoord += stukje.content
                    placeholder.markdown(
                        volledig_antwoord + "▌"
                    )

            placeholder.markdown(volledig_antwoord)

            # Alleen tonen wanneer retrieval is gebruikt
            if results:
                with st.expander(
                    "🔍 Bekijk gebruikte PDF-fragmenten"
                ):
                    for i, doc in enumerate(results, start=1):
                        st.markdown(f"**Fragment {i}**")
                        st.write(doc.page_content)
                        st.divider()

        st.session_state.gesprek.append(
            AIMessage(content=volledig_antwoord)
        )

    except Exception as fout:
        st.error(f"Er ging iets mis: {fout}")