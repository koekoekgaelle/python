from typing import Any

from assistant.aiassistant.agent import board_game_agent


def answer_question(
    question: str,
    game_id: int,
    session_id: int,
) -> dict[str, Any]:
    cleaned_question = question.strip()

    thread_id = f"game-session-{session_id}"

    if not cleaned_question:
        raise ValueError("De vraag mag niet leeg zijn.")

    if game_id <= 0:
        raise ValueError("game_id moet een geldig positief getal zijn.")

    if session_id <= 0:
        raise ValueError("session_id moet een geldig positief getal zijn.")

    result = board_game_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"game_id: {game_id}\n"
                        f"session_id: {session_id}\n"
                        f"Vraag: {cleaned_question}"
                    ),
                }
            ]
        }, 
        config={
            "configurable": {
                "thread_id": thread_id
        },
        "metadata":{
            "thread_id": thread_id,
            "game_id": game_id,
            "game_session_id": session_id
        },
        "run_name": "board_game_agent_run",
        },
    )

    messages = result.get("messages", [])

    if not messages:
        raise RuntimeError("De agent heeft geen antwoord teruggegeven.")

    final_message = messages[-1]
    answer = final_message.content

    if not answer:
        raise RuntimeError("De agent gaf een leeg antwoord terug.")

    return {
        "answer": answer,
        "messages": messages,
        "thread_id": thread_id,
    }