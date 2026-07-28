from assistant.database.supabase_client import get_supabase_client


def get_all_games():
    """
    Haal alle bordspellen op uit Supabase.
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("games")
        .select("*")
        .order("name")
        .execute()
    )

    return response.data or []


def get_game_by_id(game_id: int):
    """
    Zoek één bordspel op basis van de interne Supabase-id.
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("games")
        .select("*")
        .eq("id", game_id)
        .limit(1)
        .execute()
    )

    games = response.data or []

    if not games:
        return None

    return games[0]


def get_game_by_bgg_id(bgg_id: int):
    """
    Zoek één bordspel op basis van het BoardGameGeek-id.
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("games")
        .select("*")
        .eq("bgg_id", bgg_id)
        .limit(1)
        .execute()
    )

    games = response.data or []

    if not games:
        return None

    return games[0]


def get_game_by_slug(slug: str):
    """
    Zoek één bordspel op basis van de interne slug.
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("games")
        .select("*")
        .eq("slug", slug)
        .limit(1)
        .execute()
    )

    games = response.data or []

    if not games:
        return None

    return games[0]


def create_game(
    name: str,
    slug: str,
    bgg_id: int | None = None,
    year_published: int | None = None,
    min_players: int | None = None,
    max_players: int | None = None,
    playing_time: int | None = None,
    image_url: str | None = None,
):
    """
    Voeg een nieuw bordspel toe aan Supabase.
    """
    supabase = get_supabase_client()

    game_data = {
        "name": name,
        "slug": slug,
        "bgg_id": bgg_id,
        "year_published": year_published,
        "min_players": min_players,
        "max_players": max_players,
        "playing_time": playing_time,
        "image_url": image_url,
    }

    response = (
        supabase.table("games")
        .insert(game_data)
        .execute()
    )

    created_games = response.data or []

    if not created_games:
        raise RuntimeError(
            f"Het bordspel '{name}' kon niet worden toegevoegd."
        )

    return created_games[0]