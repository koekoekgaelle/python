from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver


from assistant.aiassistant.prompts import SYSTEM_PROMPT
from assistant.tools.player_tool import add_players
from assistant.tools.rulebook_tool import search_rulebook
from assistant.tools.score_tool import update_score


def create_board_game_agent(
        model=None,
        checkpointer=None,
):

    if model is None:
        model = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0,
        )

    if checkpointer is None:
        checkpointer = InMemorySaver()
        #bewust alleen in memory, geheugen alleen nodig tijdens een actieve spelsessie.


    return create_agent(
        model=model,
        tools=[
            add_players,
            search_rulebook,
            update_score,
        ],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,)