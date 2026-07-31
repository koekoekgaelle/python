from typing import Any

from assistant.repositories.repository_helpers import (
    insert_row,
    select_rows,
)

TABLE_NAME = "games"


def get_all_games() -> list[dict[str, Any]]:
    """Haal alle bordspellen op."""
    return select_rows(
        table_name=TABLE_NAME,
        order_by="name",
    )


def get_game_by_id(
    game_id: int,
) -> dict[str, Any] | None:
    games = select_rows(
        table_name=TABLE_NAME,
        filters={"id": game_id},
        limit=1,
    )

    return games[0] if games else None


def get_game_by_bgg_id(
    bgg_id: int,
) -> dict[str, Any] | None:
    games = select_rows(
        table_name=TABLE_NAME,
        filters={"bgg_id": bgg_id},
        limit=1,
    )

    return games[0] if games else None


def get_game_by_slug(
    slug: str,
) -> dict[str, Any] | None:
    games = select_rows(
        table_name=TABLE_NAME,
        filters={"slug": slug},
        limit=1,
    )

    return games[0] if games else None


def create_game(
    name: str,
    slug: str,
    bgg_id: int | None = None,
    year_published: int | None = None,
    min_players: int | None = None,
    max_players: int | None = None,
    playing_time: int | None = None,
    image_url: str | None = None,
) -> dict[str, Any]:
    game = insert_row(
        table_name=TABLE_NAME,
        data={
            "name": name,
            "slug": slug,
            "bgg_id": bgg_id,
            "year_published": year_published,
            "min_players": min_players,
            "max_players": max_players,
            "playing_time": playing_time,
            "image_url": image_url,
        },
    )

    return game