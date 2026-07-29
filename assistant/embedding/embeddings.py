from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def create_embeddings():
    """
    Maak een OpenAI Embedding-model aan.
    """

    return OpenAIEmbeddings(
        model="text-embedding-3-small"
    )