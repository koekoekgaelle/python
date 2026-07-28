from langchain_chroma import Chroma

from assistant.embeddings import create_embeddings


def create_vectorstore(chunks: list[str]):
    """
    Maak een lokale Chroma vector database
    en sla alle chunks erin op.
    """

    embeddings = create_embeddings()

    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory="database",
    )

    return vectorstore