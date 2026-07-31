# TODO (RensBlitz): de import "board_game_agent" hierboven wordt overschaduwd
# door de gelijknamige parameter in stream_answer(), dus deze import is dood.
# Belangrijker: stream_answer() lijkt nergens meer aangeroepen te worden, want
# app.py gebruikt answer_question() (de blocking .invoke variant) in plaats
# van deze streaming variant. Even nalopen of dit bestand nog nodig is: zo ja,
# de dode import opruimen, zo nee, dit bestand verwijderen zodat er niet twee
# manieren zijn om een antwoord van de agent te krijgen.
from langchain_core.tracers.langchain import LangChainTracer

from assistant.aiassistant.agent import board_game_agent



def stream_answer(board_game_agent, messages):
    """
    Stream een antwoord van het taalmodel.

    Geeft steeds kleine tekststukjes terug.
    """

    tracer = LangChainTracer(
        project_name="Mijn-Ai-Assistant",
    )

    for chunk in board_game_agent.stream(
        messages,
        config={
            "callbacks": [tracer],
        },
    ):
        if chunk.content:
            yield chunk.content