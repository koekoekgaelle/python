from typing import Any

from supabase import Client

from assistant.repositories.repository_helpers import insert_row
from assistant.utils.exceptions import PlayerAddError

def create_player(
    session_id: int,
    name: str,
    client: Client | None = None,
) -> dict[str, Any]:
    player = insert_row(
        table_name="session_players",
        data={
            "session_id": session_id,
            "name": name,
            "current_score": 0,
        },
        client=client,
    )

    if player is None:
        raise PlayerAddError()

    return player