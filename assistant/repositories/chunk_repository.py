from collections.abc import Sequence
from typing import Any

from langchain_core.documents import Document

from assistant.embedding_and_db.supabase_client import get_supabase_client
from assistant.repositories.repository_helpers import (
    delete_rows,
    select_rows,
)


TABLE_NAME = "document_chunks"


def create_document_chunks(
    chunks: Sequence[Document],
    embeddings: Sequence[list[float]],
    rulebook_id: int,
    game_id: int,
    batch_size: int = 50,
) -> int:
    """
    Sla documentchunks en hun embeddings op in Supabase.

    De chunks en embeddings moeten dezelfde volgorde en lengte hebben.
    De records worden in batches opgeslagen om te grote requests te voorkomen.
    """
    if len(chunks) != len(embeddings):
        raise ValueError(
            "Het aantal chunks komt niet overeen met het aantal embeddings."
        )

    if batch_size < 1:
        raise ValueError("batch_size moet minimaal 1 zijn.")

    if not chunks:
        return 0

    records = []

    for chunk, embedding in zip(chunks, embeddings):
        records.append(
            {
                "rulebook_id": rulebook_id,
                "game_id": game_id,
                "content": chunk.page_content,
                "page_number": chunk.metadata.get("page"),
                "chunk_number": chunk.metadata.get("chunk"),
                "metadata": chunk.metadata,
                "embedding": embedding,
            }
        )

    supabase = get_supabase_client()
    inserted_count = 0

    for start in range(0, len(records), batch_size):
        batch = records[start:start + batch_size]

        response = (
            supabase
            .table(TABLE_NAME)
            .insert(batch)
            .execute()
        )

        inserted_records = response.data or []

        if len(inserted_records) != len(batch):
            raise RuntimeError(
                "Niet alle documentchunks konden worden opgeslagen."
            )

        inserted_count += len(inserted_records)

    return inserted_count


def get_chunks_by_rulebook_id(
    rulebook_id: int,
) -> list[dict[str, Any]]:
    """Haal alle chunks van één handleiding op."""
    return select_rows(
        table_name=TABLE_NAME,
        columns=(
            "id, rulebook_id, game_id, content, "
            "page_number, chunk_number, metadata"
        ),
        filters={
            "rulebook_id": rulebook_id,
        },
        order_by="chunk_number",
    )


def count_chunks_by_rulebook_id(rulebook_id: int) -> int:
    """Tel hoeveel chunks voor een handleiding zijn opgeslagen."""
    supabase = get_supabase_client()

    response = (
        supabase
        .table(TABLE_NAME)
        .select("id", count="exact")
        .eq("rulebook_id", rulebook_id)
        .execute()
    )

    return response.count or 0


def delete_chunks_by_rulebook_id(rulebook_id: int) -> bool:
    """Verwijder alle chunks van één handleiding."""
    deleted_chunks = delete_rows(
        table_name=TABLE_NAME,
        filters={
            "rulebook_id": rulebook_id,
        },
    )

    return bool(deleted_chunks)