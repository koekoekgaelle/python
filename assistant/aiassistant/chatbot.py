from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from assistant.tools.rulebook_tool import search_rulebook
from assistant.tools.score_tool import update_score
from assistant.tools.player_tool import add_players
from assistant.aiassistant.prompts import SYSTEM_PROMPT


def create_chatbot():
    model = ChatOpenAI(
        model="gpt-4o-mini",
    )

    return create_agent(
        model=model,
        tools=[update_score, search_rulebook, add_players],
        system_prompt=SYSTEM_PROMPT,
    )