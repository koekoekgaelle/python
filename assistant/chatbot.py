from langchain_openai import ChatOpenAI

from assistant.prompts import SYSTEM_PROMPT


def create_chatbot():
    return ChatOpenAI(
        model="gpt-5.6",
        temperature=0.7,
    )


def create_new_conversation():
    return [SYSTEM_PROMPT]