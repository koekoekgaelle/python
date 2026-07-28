def search_documents(vectorstore, query: str, k: int = 3):
    """
    Zoek de meest relevante documenten.
    """

    return vectorstore.similarity_search(
        query=query,
        k=k,
    ) 