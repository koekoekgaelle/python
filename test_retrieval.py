from assistant.aiassistant.retriever import retrieve_relevant_chunks
from assistant.repositories.game_repository import get_game_by_bgg_id


def main():
    print("1. Catan ophalen")

    game = get_game_by_bgg_id(13)

    if not game:
        raise RuntimeError("Catan staat niet in de games-tabel.")

    print("2. Game gevonden:", game["name"])

    question = "Hoeveel zegepunten heb je nodig om te winnen?"

    print("3. Vraag:", question)
    print("4. Relevante chunks zoeken")

    chunks = retrieve_relevant_chunks(
        question=question,
        game_id=game["id"],
        match_count=17,
    )

    print("5. Aantal resultaten:", len(chunks))

    for position, chunk in enumerate(chunks, start=1):
        similarity = chunk.get("similarity") or 0
        page_number = chunk.get("page_number")
        chunk_number = chunk.get("chunk_number")
        content = chunk.get("content", "")

        clean_preview = " ".join(content.split())

        print(
            f"{position:02}. "
            f"similarity={similarity:.4f} | "
            f"pagina={page_number} | "
            f"chunk={chunk_number}" 
        )
        print(clean_preview[:200])
        print()


if __name__ == "__main__":
    main()