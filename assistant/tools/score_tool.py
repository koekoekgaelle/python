from langchain_core.tools import tool

from assistant.embedding_and_db.supabase_client import supabase


# TODO (RensBlitz): door het hele project heen gebruiken we generieke
# ValueError/RuntimeError voor domeinfouten (hier "speler niet gevonden",
# maar ook bv. "rulebook kon niet worden toegevoegd" elders). Daardoor kan een
# aanroeper niet onderscheiden wat er precies mis ging zonder de foutmelding
# te gaan parsen. Dit is belangrijk om te verbeteren: maak eigen exception-
# classes (bv. PlayerNotFoundError, InvalidScoreError) zodat callers hier
# gericht op kunnen reageren, en zodat we in app.py nettere, specifiekere
# foutmeldingen aan de gebruiker kunnen tonen.
@tool
def update_score(
    session_id: int,
    player_name: str,
    points: int,
) -> dict:
    """
    Verhoog of verlaag current_score van een bestaande speler in Supabase.

    points is de verandering:
    - 3 betekent 3 punten erbij
    - -2 betekent 2 punten eraf

    Deze tool maakt nooit een nieuwe speler aan.
    """

    cleaned_name = player_name.strip()

    if not cleaned_name:
        raise ValueError("De spelersnaam mag niet leeg zijn.")

    player_response = (
        supabase
        .table("session_players")
        .select("id, session_id, name, current_score")
        .eq("session_id", session_id)
        .ilike("name", cleaned_name)
        .limit(1)
        .execute()
    )

    if not player_response.data:
        raise ValueError(
            f"Speler '{cleaned_name}' is niet gevonden "
            f"in sessie {session_id}."
        )

    player = player_response.data[0]

    previous_score = int(player.get("current_score") or 0)
    new_score = previous_score + int(points)

    update_response = (
        supabase
        .table("session_players")
        .update({"current_score": new_score})
        .eq("id", player["id"])
        .eq("session_id", session_id)
        .execute()
    )

    if not update_response.data:
        raise RuntimeError(
            f"De score van '{cleaned_name}' kon niet worden bijgewerkt."
        )

    updated_player = update_response.data[0]

    return {
        "success": True,
        "player_id": updated_player["id"],
        "name": updated_player["name"],
        "previous_score": previous_score,
        "points_added": int(points),
        "current_score": updated_player["current_score"],
    }