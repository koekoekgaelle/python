from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from assistant.aiassistant.prompts import SYSTEM_PROMPT
from assistant.tools.player_tool import add_players
from assistant.tools.rulebook_tool import search_rulebook
from assistant.tools.score_tool import update_score


model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
)

board_game_agent = create_agent(
    model=model,
    tools=[
        search_rulebook,
        update_score,
        add_players,
    ],
    system_prompt=SYSTEM_PROMPT,
)