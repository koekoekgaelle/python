from pathlib import Path

from assistant.embedding.document_loader import load_pdf
from assistant.embedding.chunker import create_chunks


class LocalUploadedFile:
    def __init__(self, file_path: str):
        self.path = Path(file_path)
        self.name = self.path.name
        self.size = self.path.stat().st_size

    def getvalue(self) -> bytes:
        return self.path.read_bytes()


def main():
    print("1. Test gestart")

    uploaded_file = LocalUploadedFile(
        "documents/catan_handleiding.pdf"
    )

    print("2. PDF gevonden:", uploaded_file.name)

    documents = load_pdf(uploaded_file)
    print("3. Aantal pagina's:", len(documents))

    chunks = create_chunks(documents)
    print("4. Aantal chunks:", len(chunks))

    if chunks:
        first_chunk = chunks[0]

        print("5. Eerste chunknummer:", first_chunk.metadata.get("chunk"))
        print("6. Paginanummer:", first_chunk.metadata.get("page"))
        print("7. Lengte eerste chunk:", len(first_chunk.page_content))

        print("\nEerste chunk:")
        print(first_chunk.page_content[:500])


if __name__ == "__main__":
    main()