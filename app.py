import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY ontbreekt in het .env-bestand.")
    st.stop()


st.set_page_config(
    page_title="Mijn AI-assistent",
    page_icon="🤖",
)

st.title("🤖 Mijn AI-assistent")


chatbot = ChatOpenAI(
    model="gpt-5.6",
)


if "gesprek" not in st.session_state:
    st.session_state.gesprek = [
        SystemMessage(
            content=(
                "Je bent een vriendelijke AI-assistent. "
                "Je antwoordt in het Nederlands en legt dingen duidelijk uit."
            )
        )
    ]


for bericht in st.session_state.gesprek:
    if isinstance(bericht, HumanMessage):
        with st.chat_message("user"):
            st.write(bericht.content)

    elif isinstance(bericht, AIMessage):
        with st.chat_message("assistant"):
            st.write(bericht.content)


vraag = st.chat_input("Typ hier je vraag")

if vraag:
    st.session_state.gesprek.append(HumanMessage(content=vraag))

    with st.chat_message("user"):
        st.write(vraag)

    try:
        antwoord = chatbot.invoke(st.session_state.gesprek)

        st.session_state.gesprek.append(
            AIMessage(content=antwoord.content)
        )

        with st.chat_message("assistant"):
            st.write(antwoord.content)

    except Exception as fout:
        st.error(f"Er ging iets mis: {fout}")