from assistant.chunker import create_chunks
from assistant.document_loader import load_pdf
from assistant.vectordb import create_vectorstore


def process_pdf(uploaded_file):
    """
    Verwerk een geüploade PDF en maak een vectorstore.
    """

    documents = load_pdf(uploaded_file)
    chunks = create_chunks(documents)
    vectorstore = create_vectorstore(chunks)

    return {
        "vectorstore": vectorstore,
        "document_name": uploaded_file.name,
        "document_id": f"{uploaded_file.name}-{uploaded_file.size}",
        "chunk_count": len(chunks),
    }