from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver


from assistant.aiassistant.prompts import SYSTEM_PROMPT
from assistant.tools.player_tool import add_players
from assistant.tools.rulebook_tool import search_rulebook
from assistant.tools.score_tool import update_score


# TODO (RensBlitz): model, checkpointer en board_game_agent worden nu allemaal
# op module-niveau aangemaakt, dus zodra dit bestand geimporteerd wordt, wordt
# er meteen een echte OpenAI-client gebouwd. Dat maakt dit lastig te unit-
# testen (je kan niks mocken zonder rare importtrucs) en verstopt configuratie
# in importvolgorde. Overweeg hier een factory-functie van te maken (bv.
# create_board_game_agent(model=..., checkpointer=...)) die je expliciet
# aanroept vanuit app.py, dat is belangrijk voor testbaarheid. Let ook op dat
# InMemorySaver() betekent dat alle gespreksgeschiedenis verloren gaat zodra de
# app herstart/opnieuw deployed - is dat gewenst?
model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
)

checkpointer = InMemorySaver()

board_game_agent = create_agent(
    model=model,
    tools=[
        search_rulebook,
        update_score,
        add_players,
    ],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)