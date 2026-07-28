from langchain_chroma import Chroma
from langchain_core.documents import Document

from assistant.embeddings import create_embeddings


def create_vectorstore(chunks: list[Document]):
    """
    Maak een lokale Chroma vector database
    en sla alle chunks inclusief metadata erin op.
    """

    embeddings = create_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="database",
    )

    return vectorstore