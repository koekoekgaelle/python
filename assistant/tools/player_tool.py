from langchain_core.tools import tool

from assistant.repositories.player_repository import create_player


@tool
def add_players(
    session_id: int,
    player_names: list[str],
) -> list[dict]:
    """Voeg één of meerdere spelers toe aan de huidige bordspelsessie."""

    players = []

    for name in player_names:
        cleaned_name = name.strip()

        if not cleaned_name:
            continue

        player = create_player(
            session_id=session_id,
            name=cleaned_name,
        )

        players.append(
            {
                "player_id": player["id"],
                "name": player["name"],
                "current_score": player["current_score"],
            }
        )

    if not players:
        raise ValueError("Er is geen geldige spelersnaam opgegeven.")

    return players