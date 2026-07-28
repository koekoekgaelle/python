import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from assistant.chatbot import create_chatbot, create_new_conversation


load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY ontbreekt in het .env-bestand.")
    st.stop()


st.set_page_config(
    page_title="Mijn AI-assistent",
    page_icon="🤖",
)

st.title("🤖 Mijn AI-assistent")


if "gesprek" not in st.session_state:
    st.session_state.gesprek = create_new_conversation()


chatbot = create_chatbot()


for bericht in st.session_state.gesprek:
    if isinstance(bericht, HumanMessage):
        with st.chat_message("user"):
            st.write(bericht.content)

    elif isinstance(bericht, AIMessage):
        with st.chat_message("assistant"):
            st.write(bericht.content)


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