from pathlib import Path

from assistant.embedding.document_service import process_pdf
from assistant.repositories.game_repository import get_game_by_bgg_id


class LocalUploadedFile:
    def __init__(self, file_path: str):
        self.path = Path(file_path)
        self.name = self.path.name
        self.size = self.path.stat().st_size

    def getvalue(self) -> bytes:
        return self.path.read_bytes()


def main():
    print("1. Catan ophalen uit Supabase")

    game = get_game_by_bgg_id(13)

    if not game:
        raise RuntimeError("Catan staat niet in de games-tabel.")

    print("2. Game gevonden:", game["name"])

    uploaded_file = LocalUploadedFile(
        "documents/catan_handleiding.pdf"
    )

    print("3. Handleiding verwerken")

    result = process_pdf(
        uploaded_file=uploaded_file,
        game_id=game["id"],
        language="nl",
        document_type="rulebook",
    )

    print("4. Import geslaagd")
    print("Rulebook ID:", result["rulebook_id"])
    print("Bestand:", result["document_name"])
    print("Aantal opgeslagen chunks:", result["chunk_count"])


if __name__ == "__main__":
    main()