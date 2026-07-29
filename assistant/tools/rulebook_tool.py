from langchain_core.tools import tool

from assistant.aiassistant.retriever import retrieve_relevant_chunks


@tool
def search_rulebook(
    question: str,
    game_id: int,
) -> list[dict]:
    """Zoek relevante spelregels in de handleiding."""

    return retrieve_relevant_chunks(
        question=question,
        game_id=game_id,
        match_count=5,
    )