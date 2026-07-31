from typing import Any

from assistant.embedding_and_db.chunker import create_chunks
from assistant.embedding_and_db.document_loader import load_pdf
from assistant.embedding_and_db.ocr_service import load_pdf_with_ocr
from assistant.embedding_and_db.embeddings import create_embeddings
from assistant.utils.exceptions import InvalidContentError, ChunkCreationError
from assistant.repositories.chunk_repository import create_document_chunks
from assistant.repositories.rulebook_repository import (
    create_rulebook,
    delete_rulebook,
)


def process_pdf(
    uploaded_file: Any,
    game_id: int,
    language: str = "nl",
    document_type: str = "rulebook",
)-> dict[str, Any]:
    """
    Verwerk een PDF-handleiding en sla de chunks op.

    Als opslaan mislukt nadat het rulebook is aangemaakt,
    wordt het rulebook weer verwijderd.
    """

    documents = extract_text_from_pdf(uploaded_file=uploaded_file, language=language)
    chunks = create_rulebook_chunks(documents)

    rulebook = None

    try:
        rulebook = create_rulebook(
            game_id=game_id,
            document_type=document_type,
            file_name=uploaded_file.name,
            language=language,
        )

        rulebook_id = rulebook["id"]

        add_chunk_metadata(
            chunks=chunks,
            game_id=game_id,
            rulebook_id=rulebook_id,
            file_name=uploaded_file.name,
            language=language,
            document_type=document_type,
        )

        inserted_count = persist_rulebook_chunks(
            chunks=chunks,
            rulebook_id=rulebook_id,
            game_id=game_id,
        )       

        return build_process_result(
            rulebook=rulebook,
            game_id=game_id,
            file_name=uploaded_file.name,
            inserted_count=inserted_count,
        )

    except Exception:
        if rulebook is not None:
            delete_rulebook(rulebook_id=rulebook["id"])

        raise

def extract_text_from_pdf(
    uploaded_file,
    language: str,
)-> list:
    """lees tekst uit pdf en gebruik ocr als fallback"""
    documents = load_pdf(uploaded_file)

    if documents_have_text(documents):
        print("✅ Native PDF-extractie gebruikt")
        return documents

    print("⚠️ Geen tekst gevonden in PDF, OCR wordt gebruikt")

    documents = load_pdf_with_ocr(
        uploaded_file,
        language=language,
    )

    if not documents_have_text(documents):
        raise InvalidContentError()

    return documents 

def documents_have_text(documents: list) -> bool:
    """Controleer of de documenten tekst bevatten."""                           
    return any(doc.page_content.strip() for doc in documents)

def create_rulebook_chunks(documents: list) -> list:
    """Maak chunks van de documenten."""
    chunks= create_chunks(documents)

    if not chunks:
        raise ChunkCreationError( )
    return chunks


def add_chunk_metadata(
    chunks: list,
    game_id: int,
    rulebook_id: int,
    file_name: str,
    language: str,
    document_type: str,
) -> None:
    """Voeg metadata toe aan de chunks."""
    metadata = {
        "game_id": game_id,
        "rulebook_id": rulebook_id,
        "file_name": file_name,
        "language": language,
        "document_type": document_type,
    }
    for chunk in chunks:
        chunk.metadata.update(metadata)

def persist_rulebook_chunks(
        chunks: list,
        rulebook_id: int,
        game_id: int,
        embedding_model: Any | None = None,
) -> int:
    if embedding_model is None:
        embedding_model = create_embeddings()
    
    texts = [chunk.page_content for chunk in chunks]
    vectors = embedding_model.embed_documents(texts)

    return create_document_chunks(
        chunks=chunks,
        embeddings=vectors,
        rulebook_id=rulebook_id,
        game_id=game_id,
    )

def build_process_result(
        rulebook: dict,
        game_id: int,
        file_name: str,
        inserted_count: int,
) -> dict[str, Any]:
    """maak het resultaat van pdf verwerking aan"""
    rulebook_id = rulebook["id"]

    return {
        "rulebook": rulebook,
        "rulebook_id": rulebook_id,
        "game_id": game_id,
        "file_name": file_name,
        "chunk_count": inserted_count,
    }