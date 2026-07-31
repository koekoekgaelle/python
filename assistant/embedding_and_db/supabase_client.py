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


# TODO (RensBlitz): we hebben nu 2 manieren om aan de Supabase-client te komen:
# deze losse "supabase" singleton en de functie get_supabase_client() zelf.
# In de repositories wordt het door elkaar gebruikt (player_repository.py en
# score_tool.py pakken "supabase" direct, terwijl game_repository.py,
# rulebook_repository.py en chunk_repository.py steeds get_supabase_client()
# aanroepen). Kies 1 manier en gebruik die overal, dat maakt het consistenter
# en makkelijker om later te mocken in tests. Daarnaast staat in bijna elke
# repository dezelfde .table(...).select/insert/eq(...).execute() code - dat
# zou je kunnen samenvoegen in een klein herbruikbaar hulpfunctie/baseclass,
# dat scheelt een hoop duplicate code. Dit is belangrijk voor de onderhoudbaarheid
# op de lange termijn, al is het geen acute bug.
supabase = get_supabase_client()