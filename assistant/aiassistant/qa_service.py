from typing import Any
from assistant.utils.exceptions import NoAnswerError

def answer_question(
    agent: Any,
    question: str,
    game_id: int,
    session_id: int,
    callbacks: list[Any] | None = None,
) -> str:
    config: dict[str, Any] = {
        "configurable": {
            "thread_id": f"game-session-{session_id}",
        },
        "metadata": {
            "thread_id": f"game-session-{session_id}",
            "game_id": game_id,
            "game_session_id": session_id,
        },
        "run_name": "board_game_agent_run",
    }

    if callbacks:
        config["callbacks"] = callbacks

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"game_id: {game_id}\n"
                        f"session_id: {session_id}\n"
                        f"Vraag: {question}"
                    ),
                }
            ]
        },
        config=config,
    )

    messages = result["messages"]
    final_message = messages[-1]
    answer = final_message.content

    if not isinstance(answer, str) or not answer.strip():
        raise NoAnswerError()

    return answer.strip()