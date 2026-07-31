from assistant.embedding_and_db.chunker import create_chunks
from assistant.embedding_and_db.document_loader import load_pdf
from assistant.embedding_and_db.ocr_service import load_pdf_with_ocr
from assistant.embedding_and_db.embeddings import create_embeddings
from assistant.repositories.chunk_repository import create_document_chunks
from assistant.repositories.rulebook_repository import (
    create_rulebook,
    delete_rulebook,
)


def process_pdf(
    uploaded_file,
    game_id: int,
    language: str = "nl",
    document_type: str = "rulebook",
):
    """
    Verwerk een PDF-handleiding en sla deze op in Supabase.

    Stappen:
    1. PDF uitlezen
    2. Tekst opdelen in chunks
    3. Metadata toevoegen
    4. Embeddings genereren
    5. Rulebook-record aanmaken
    6. Chunks en embeddings opslaan

    Bij een fout wordt het aangemaakte rulebook weer verwijderd.
    Door ON DELETE CASCADE worden gekoppelde chunks ook verwijderd.
    """

    # TODO (RensBlitz): process_pdf() doet nu te veel in 1 functie (PDF inlezen,
    # OCR-fallback bepalen, chunken, metadata toevoegen, embeddings maken, en
    # opslaan/rollback in de database) - dit is lastig te testen en te lezen.
    # Splits dit op in kleinere stappen, bv. een aparte extract_text_from_pdf()
    # die de OCR-fallback regelt, en een aparte persist_rulebook_chunks().
    # Daarnaast wordt hieronder 2x dezelfde check gedaan (heeft "documents"
    # tekst of niet), waardoor OCR in het slechtste geval 2x wordt aangeroepen
    # voor hetzelfde bestand. Dit is belangrijk om recht te trekken, want dat
    # kost onnodig extra tijd (en OCR is al traag) en maakt de flow verwarrend.
    rulebook = None

    try:
        documents = load_pdf(uploaded_file)

        if any(doc.page_content.strip() for doc in documents):
            print("✅ Native PDF extractie gebruikt")
        else:
            print("⚠️ Geen tekst gevonden in PDF, OCR wordt gebruikt")
            documents = load_pdf_with_ocr(
                uploaded_file,
                language=language,
            )

        has_text = any(
            doc.page_content.strip()
            for doc in documents
        )

        if not has_text:
            documents = load_pdf_with_ocr(
                uploaded_file,
                language=language,
            )

        chunks = create_chunks(documents)

        if not chunks:
            raise ValueError(
                "Er konden geen tekstchunks uit de PDF worden gemaakt."
            )

        rulebook = create_rulebook(
            game_id=game_id,
            filename=uploaded_file.name,
            language=language,
            document_type=document_type,
        )

        rulebook_id = rulebook["id"]

        for chunk in chunks:
            chunk.metadata.update(
                {
                    "game_id": game_id,
                    "rulebook_id": rulebook_id,
                    "filename": uploaded_file.name,
                    "language": language,
                    "document_type": document_type,
                }
            )

        embedding_model = create_embeddings()

        texts = [
            chunk.page_content
            for chunk in chunks
        ]

        vectors = embedding_model.embed_documents(texts)

        inserted_count = create_document_chunks(
            chunks=chunks,
            embeddings=vectors,
            rulebook_id=rulebook_id,
            game_id=game_id,
        )

        return {
            "rulebook": rulebook,
            "rulebook_id": rulebook_id,
            "game_id": game_id,
            "document_name": uploaded_file.name,
            "document_id": (
                f"{game_id}-{rulebook_id}-{uploaded_file.name}"
            ),
            "chunk_count": inserted_count,
        }

    except Exception:
        if rulebook is not None:
            delete_rulebook(rulebook["id"])

        raise