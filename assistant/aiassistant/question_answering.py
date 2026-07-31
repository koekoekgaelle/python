from typing import Any

from langchain_core.tracers.langchain import LangChainTracer

#had chat_service nog niet verwijderd omdat daar mijn langsmith configuratie zat, maar die heb ik nu hier toegevoegd. 


def answer_question(
    agent: Any,
    question: str,
    game_id: int,
    session_id: int,
    callbacks: list [Any] | None = None,
    )-> dict[str, Any]:
    config= {
        "configurable": {
            "thread_id": f"game-session-{session_id}"
        },
        "metadata": {
            "thread_id": f"game-session-{session_id}",
            "game_id": game_id,
            "game_session_id": session_id
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
    