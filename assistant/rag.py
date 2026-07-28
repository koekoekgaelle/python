from langchain_core.messages import HumanMessage

from assistant.retriever import search_documents


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