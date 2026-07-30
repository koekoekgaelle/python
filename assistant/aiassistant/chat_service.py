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