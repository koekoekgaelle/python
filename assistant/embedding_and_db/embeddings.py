from langchain_openai import OpenAIEmbeddings


def create_embeddings():
    """
    Maak een OpenAI Embedding-model aan.
    """

    return OpenAIEmbeddings(
        model="text-embedding-3-small"
    )