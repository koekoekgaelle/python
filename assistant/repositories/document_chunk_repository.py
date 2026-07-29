from typing import Any

from assistant.database.supabase_client import get_supabase_client


def match_document_chunks(
    query_embedding: list[float],
    game_id: int | None = None,
    match_count: int = 5,
) -> list[dict[str, Any]]:
    """
    Zoek documentchunks die inhoudelijk lijken op de query-embedding.

    Args:
        query_embedding:
            De embeddingvector van de gebruikersvraag.

        game_id:
            Beperk de zoekresultaten optioneel tot één spel.

        match_count:
            Het maximale aantal resultaten.

    Returns:
        Een lijst met overeenkomstige documentchunks.
    """

    if not query_embedding:
        raise ValueError("query_embedding mag niet leeg zijn.")

    if match_count < 1:
        raise ValueError("match_count moet minimaal 1 zijn.")

    supabase = get_supabase_client()

    response = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": query_embedding,
            "filter_game_id": game_id,
            "match_count": match_count,
        },
    ).execute()

    return response.data or []