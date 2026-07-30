import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Maak en retourneer één Supabase-client.

    De URL en secret key worden uit het .env-bestand gelezen.
    """

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SECRET_KEY")

    if not supabase_url:
        raise ValueError("SUPABASE_URL ontbreekt in het .env-bestand.")

    if not supabase_key:
        raise ValueError(
            "SUPABASE_SECRET_KEY ontbreekt in het .env-bestand."
        )

    return create_client(supabase_url, supabase_key)


supabase = get_supabase_client()