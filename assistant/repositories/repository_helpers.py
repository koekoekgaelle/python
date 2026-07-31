from typing import Any

from supabase import Client

from assistant.embedding_and_db.supabase_client import get_supabase_client



def get_client(client: Client | None = None) -> Client:
    """
    Geef de meegegeven Supabase-client terug.

    Als er geen client is meegegeven, wordt de standaard
    gecachete Supabase-client gebruikt.
    """
    return client or get_supabase_client()


def select_rows(
    table_name: str,
    columns: str = "*",
    filters: dict[str, Any] | None = None,
    limit: int | None = None,
    order_by: str | None = None,
    descending: bool = False,
    client: Client | None = None,
) -> list[dict[str, Any]]:
    """
    Haal rijen op uit een Supabase-tabel.

    Ondersteunt eenvoudige gelijkheidsfilters, sortering en een limiet.
    """
    supabase = get_client(client)

    query = supabase.table(table_name).select(columns)

    for column, value in (filters or {}).items():
        query = query.eq(column, value)

    if order_by is not None:
        query = query.order(
            order_by,
            desc=descending,
        )

    if limit is not None:
        query = query.limit(limit)

    response = query.execute()

    return response.data or []


def insert_row(
    table_name: str,
    data: dict[str, Any],
    client: Client | None = None,
) -> dict[str, Any] | None:
    """
    Voeg één rij toe en geef de aangemaakte rij terug.
    """
    supabase = get_client(client)

    response = (
        supabase
        .table(table_name)
        .insert(data)
        .execute()
    )

    rows = response.data or []

    if not rows:
        return None

    return rows[0]


def delete_rows(
    table_name: str,
    filters: dict[str, Any],
    client: Client | None = None,
) -> list[dict[str, Any]]:
    """
    Verwijder rijen die voldoen aan de opgegeven filters.
    """
    supabase = get_client(client)

    query = supabase.table(table_name).delete()

    for column, value in filters.items():
        query = query.eq(column, value)

    response = query.execute()

    return response.data or []