from typing import Any

from assistant.embedding.embeddings import create_embeddings
from assistant.repositories.document_chunk_repository import (
    match_document_chunks,
)


def retrieve_relevant_chunks(
    question: str,
    game_id: int | None = None,
    match_count: int = 5,
) -> list[dict[str, Any]]:
    """
    Zoek relevante rulebook-chunks voor een gebruikersvraag.

    Eerst wordt de vraag omgezet naar een embedding.
    Daarna zoekt Supabase naar vergelijkbare chunks.
    """

    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("De vraag mag niet leeg zijn.")

    embedding_model = create_embeddings()

    query_embedding = embedding_model.embed_query(cleaned_question)

    return match_document_chunks(
        query_embedding=query_embedding,
        game_id=game_id,
        match_count=match_count,
    ) 