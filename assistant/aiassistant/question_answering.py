from langchain_openai import ChatOpenAI

from assistant.aiassistant.retriever import retrieve_relevant_chunks


def answer_question(
    question: str,
    game_id: int,
    match_count: int = 5,
) -> dict:
    """
    Beantwoord een spelregelvraag met context uit Supabase.
    """

    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("De vraag mag niet leeg zijn.")

    chunks = retrieve_relevant_chunks(
        question=cleaned_question,
        game_id=game_id,
        match_count=match_count,
    )

    if not chunks:
        return {
            "answer": "Ik kon hierover niets vinden in de handleiding.",
            "sources": [],
        }

    context_parts = []

    for index, chunk in enumerate(chunks, start=1):
        page_number = chunk.get("page_number")
        content = chunk.get("content", "")

        context_parts.append(
            f"[Bron {index}, pagina {page_number}]\n{content}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
Je bent een assistent voor bordspelregels.

Beantwoord de vraag uitsluitend met de informatie uit de bronnen hieronder.

Regels:
- Verzin geen informatie.
- Geef duidelijk aan wanneer de bronnen onvoldoende informatie bevatten.
- Antwoord in het Nederlands.
- Houd het antwoord begrijpelijk en beknopt.
- Vermeld achter relevante beweringen de bron, bijvoorbeeld [Bron 1, pagina 2].

Vraag:
{cleaned_question}

Bronnen:
{context}
"""

    model = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
    )

    response = model.invoke(prompt)

    sources = [
        {
            "page_number": chunk.get("page_number"),
            "chunk_number": chunk.get("chunk_number"),
            "similarity": chunk.get("similarity"),
            "content": chunk.get("content", ""),
        }
        for chunk in chunks
    ]

    return {
        "answer": response.content,
        "sources": sources,
    }