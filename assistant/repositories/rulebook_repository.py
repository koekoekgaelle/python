from assistant.database.supabase_client import get_supabase_client


def get_rulebooks_by_game_id(game_id: int):
    """
    Haal alle handleidingen op die bij één bordspel horen.
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("rulebooks")
        .select("*")
        .eq("game_id", game_id)
        .order("uploaded_at", desc=True)
        .execute()
    )

    return response.data or []


def get_rulebook_by_id(rulebook_id: int):
    """
    Zoek één handleiding op basis van de interne Supabase-id.
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("rulebooks")
        .select("*")
        .eq("id", rulebook_id)
        .limit(1)
        .execute()
    )

    rulebooks = response.data or []

    if not rulebooks:
        return None

    return rulebooks[0]


def rulebook_exists(game_id: int) -> bool:
    """
    Controleer of er minimaal één handleiding voor een spel bestaat.
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("rulebooks")
        .select("id")
        .eq("game_id", game_id)
        .limit(1)
        .execute()
    )

    return bool(response.data)


def create_rulebook(
    game_id: int,
    filename: str,
    language: str = "nl",
    document_type: str = "rulebook",
):
    """
    Voeg een nieuwe handleiding toe aan Supabase.
    """
    supabase = get_supabase_client()

    rulebook_data = {
        "game_id": game_id,
        "filename": filename,
        "language": language,
        "document_type": document_type,
    }

    response = (
        supabase.table("rulebooks")
        .insert(rulebook_data)
        .execute()
    )

    created_rulebooks = response.data or []

    if not created_rulebooks:
        raise RuntimeError(
            f"De handleiding '{filename}' kon niet worden toegevoegd."
        )

    return created_rulebooks[0]


def delete_rulebook(rulebook_id: int):
    """
    Verwijder een handleiding.

    Door de foreign key met ON DELETE CASCADE worden later ook de
    bijbehorende document-chunks verwijderd.
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("rulebooks")
        .delete()
        .eq("id", rulebook_id)
        .execute()
    )

    deleted_rulebooks = response.data or []

    if not deleted_rulebooks:
        return False

    return True