from typing import Any

from supabase import Client

from assistant.repositories.repository_helpers import (
    delete_rows,
    insert_row,
    select_rows,
)


TABLE_NAME = "rulebooks"


def get_rulebooks_by_game_id(
    game_id: int,
    client: Client | None = None,
) -> list[dict[str, Any]]:
    """
    Haal alle handleidingen op die bij één bordspel horen.
    """
    return select_rows(
        table_name=TABLE_NAME,
        filters={
            "game_id": game_id,
        },
        order_by="uploaded_at",
        descending=True,
        client=client,
    )


def get_rulebook_by_id(
    rulebook_id: int,
    client: Client | None = None,
) -> dict[str, Any] | None:
    """
    Zoek één handleiding op basis van de interne Supabase-id.
    """
    rulebooks = select_rows(
        table_name=TABLE_NAME,
        filters={
            "id": rulebook_id,
        },
        limit=1,
        client=client,
    )

    if not rulebooks:
        return None

    return rulebooks[0]


def rulebook_exists(
    game_id: int,
    client: Client | None = None,
) -> bool:
    """
    Controleer of er minimaal één handleiding voor een spel bestaat.
    """
    rulebooks = select_rows(
        table_name=TABLE_NAME,
        columns="id",
        filters={
            "game_id": game_id,
        },
        limit=1,
        client=client,
    )

    return bool(rulebooks)


def create_rulebook(
    game_id: int,
    filename: str,
    language: str = "nl",
    document_type: str = "rulebook",
    client: Client | None = None,
) -> dict[str, Any]:
    """
    Voeg een nieuwe handleiding toe aan Supabase.
    """
    rulebook_data = {
        "game_id": game_id,
        "filename": filename,
        "language": language,
        "document_type": document_type,
    }

    created_rulebook = insert_row(
        table_name=TABLE_NAME,
        data=rulebook_data,
        client=client,
    )

    if created_rulebook is None:
        raise RuntimeError(
            f"De handleiding '{filename}' kon niet worden toegevoegd."
        )

    return created_rulebook


def delete_rulebook(
    rulebook_id: int,
    client: Client | None = None,
) -> bool:
    """
    Verwijder een handleiding.

    Door de foreign key met ON DELETE CASCADE worden ook de
    bijbehorende document-chunks verwijderd.
    """
    deleted_rulebooks = delete_rows(
        table_name=TABLE_NAME,
        filters={
            "id": rulebook_id,
        },
        client=client,
    )

    return bool(deleted_rulebooks)