# TODO (RensBlitz): deze import klopt niet, "search_documents" bestaat niet in
# retriever.py (daar heet de functie "retrieve_relevant_chunks"), dus dit
# bestand crasht zodra het geimporteerd wordt. Daarnaast lijkt build_rag_messages
# hier niet meer gebruikt te worden, omdat de agent nu via de search_rulebook
# tool werkt in plaats van via deze losse RAG-flow. Dit is belangrijk om op te
# lossen: of dit bestand bijwerken en echt gebruiken, of helemaal verwijderen,
# want twee losse implementaties voor hetzelfde (ophalen van context) zorgt
# voor verwarring en onderhoudswerk.
from langchain_core.messages import HumanMessage

from assistant.aiassistant.retriever import search_documents


def build_rag_messages(
    conversation,
    question,
    vectorstore,
    k=3,
):
    """
    Bouw de berichten die naar GPT gestuurd worden
    met behulp van Retrieval-Augmented Generation.
    """

    results = search_documents(
        vectorstore,
        question,
        k=k,
    )

    context = "\n\n---\n\n".join(
        doc.page_content
        for doc in results
    )

    rag_question = HumanMessage(
        content=f"""
Gebruik de onderstaande context om de vraag te beantwoorden.

Als het antwoord niet in de context staat,
zeg dan eerlijk dat je het niet weet.

CONTEXT:
{context}

VRAAG:
{question}
"""
    )

    messages = conversation[:-1] + [rag_question]

    return messages, results