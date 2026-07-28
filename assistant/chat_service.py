def stream_answer(chatbot, messages):
    """
    Stream een antwoord van het taalmodel.

    Geeft steeds kleine tekststukjes terug.
    """

    for chunk in chatbot.stream(messages):
        if chunk.content:
            yield chunk.content