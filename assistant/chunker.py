from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(documents: list[Document]) -> list[Document]:
    """
    Verdeel PDF-pagina's in kleinere overlappende chunks.

    De metadata van iedere pagina blijft behouden.
    Iedere chunk krijgt daarnaast een chunknummer.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    chunks = splitter.split_documents(documents)

    for chunk_number, chunk in enumerate(chunks, start=1):
        chunk.metadata["chunk"] = chunk_number

    return chunks