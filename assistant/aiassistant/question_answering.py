from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from assistant.aiassistant.retriever import retrieve_relevant_chunks
from assistant.tools.score_tool import update_score
from assistant.prompts import SYSTEM_PROMPT


model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
)

agent = create_agent(
    model=model,
    tools=[update_score],
    system_prompt=SYSTEM_PROMPT,
)


def answer_question(
    question: str,
    game_id: int,
    match_count: int = 5,
) -> dict:
    """
    Beantwoord een spelregelvraag met context uit Supabase.
    """

    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("De vraag mag niet leeg zijn.")

    chunks = retrieve_relevant_chunks(
        question=cleaned_question,
        game_id=game_id,
        match_count=match_count,
    )

    if not chunks:
        return {
            "answer": "Ik kon hierover niets vinden in de handleiding.",
            "sources": [],
        }

    context_parts = []

    for index, chunk in enumerate(chunks, start=1):
        page_number = chunk.get("page_number")
        content = chunk.get("content", "")

        context_parts.append(
            f"[Bron {index}, pagina {page_number}]\n{content}"
        )

    context = "\n\n".join(context_parts)

    user_message = f"""
Vraag:
{cleaned_question}

Bronnen uit de handleiding:
{context}
"""

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                }
            ]
        }
    )

    final_message = result["messages"][-1]

    sources = [
        {
            "page_number": chunk.get("page_number"),
            "chunk_number": chunk.get("chunk_number"),
            "similarity": chunk.get("similarity"),
            "content": chunk.get("content", ""),
        }
        for chunk in chunks
    ]

    return {
        "answer": final_message.content,
        "sources": sources,
    }