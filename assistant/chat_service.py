from langchain_core.tracers.langchain import LangChainTracer


def stream_answer(chatbot, messages):
    """
    Stream een antwoord van het taalmodel.

    Geeft steeds kleine tekststukjes terug.
    """

    tracer = LangChainTracer(
        project_name="Mijn-Ai-Assistant",
    )

    for chunk in chatbot.stream(
        messages,
        config={
            "callbacks": [tracer],
        },
    ):
        if chunk.content:
            yield chunk.content