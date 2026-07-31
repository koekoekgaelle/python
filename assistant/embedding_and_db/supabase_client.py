import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import Client, create_client
from assistant.utils.exceptions import SupabaseUrlError, SupabaseKeyError

load_dotenv()


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Maak en retourneer één gechachete Supabase-client.

    De URL en secret key worden uit het .env-bestand gelezen.
    """

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SECRET_KEY")

    if not supabase_url:
        raise SupabaseUrlError()

    if not supabase_key:
        raise SupabaseKeyError()

    return create_client(supabase_url, supabase_key)
