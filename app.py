import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from langchain_core.messages import AIMessage, HumanMessage

from assistant.chatbot import create_chatbot, create_new_conversation
from assistant.chat_service import stream_answer
from assistant.document_service import process_pdf
from assistant.rag import build_rag_messages

# =========================
# Configuratie
# =========================



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
        type=["pdf"],
    )

    gebruik_pdf = st.checkbox(
         "Gebruik de PDF voor mijn vragen",
           value=True,
           disabled=uploaded_file is None,
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

    if st.session_state.get("document_id") != document_id:
        document_data = process_pdf(uploaded_file)

        st.session_state.vectorstore = document_data["vectorstore"]
        st.session_state.document_id = document_data["document_id"]
        st.session_state.document_name = document_data["document_name"]
        st.session_state.aantal_chunks = document_data["chunk_count"]

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

        if ("vectorstore" in st.session_state and gebruik_pdf):
            berichten_voor_model, results = build_rag_messages(
                st.session_state.gesprek,
                vraag,
                st.session_state.vectorstore,
            )

        else:
            results = []
            berichten_voor_model = st.session_state.gesprek

        # =========================
        # Antwoord genereren
        # =========================

        with st.chat_message("assistant"):
            volledig_antwoord = ""
            placeholder = st.empty()

            for stukje in stream_answer(
                chatbot,
                berichten_voor_model,
            ):
                volledig_antwoord += stukje

                placeholder.markdown(
                    volledig_antwoord + "▌"
                )

            placeholder.markdown(volledig_antwoord)

            # Alleen tonen wanneer retrieval is gebruikt
            if results:
                st.markdown("### 📚 Bronnen")

                gebruikte_bronnen = set()

                for doc in results:
                    source = doc.metadata.get(
                        "source",
                        "Onbekende bron",
                    )
                    page = doc.metadata.get(
                        "page",
                        "Onbekend",
                    )

                    bron = (source, page)

                    if bron not in gebruikte_bronnen:
                        st.caption(
                            f"📄 {source} — pagina {page}"
                        )
                        gebruikte_bronnen.add(bron)

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