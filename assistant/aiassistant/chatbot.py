from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from assistant.tools.score_tool import update_score
from assistant.prompts import SYSTEM_PROMPT


def create_chatbot():
    model = ChatOpenAI(
        model="gpt-4o-mini",
    )

    return create_agent(
        model=model,
        tools=[update_score],
        system_prompt=SYSTEM_PROMPT,
    )