from assistant.embedding_and_db.supabase_client import supabase


def create_player(
    session_id: int,
    name: str,
) -> dict:
    response = (
        supabase.table("session_players")
        .insert(
            {
                "session_id": session_id,
                "name": name,
                "current_score": 0,
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError("De speler kon niet worden toegevoegd.")

    return response.data[0]