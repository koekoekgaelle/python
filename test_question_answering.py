from assistant.aiassistant.question_answering import answer_question
from assistant.repositories.game_repository import get_game_by_bgg_id


def main():
    print("1. Catan ophalen")

    game = get_game_by_bgg_id(13)

    if not game:
        raise RuntimeError("Catan staat niet in de database.")

    question = "Hoeveel zegepunten heb je nodig om te winnen?"

    print("2. Vraag:", question)
    print("3. Antwoord genereren")

    result = answer_question(
        question=question,
        game_id=game["id"],
        match_count=15,
    )

    print("\nANTWOORD")
    print("=" * 70)
    print(result["answer"])

    print("\nGEBRUIKTE BRONNEN")
    print("=" * 70)

    for index, source in enumerate(result["sources"], start=1):
        similarity = source.get("similarity") or 0

        print(
            f"Bron {index} | "
            f"pagina {source['page_number']} | "
            f"chunk {source['chunk_number']} | "
            f"similarity {similarity:.4f}"
        )


if __name__ == "__main__":
    main()