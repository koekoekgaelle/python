from langchain_core.messages import SystemMessage


SYSTEM_PROMPT = SystemMessage(
    content=(
        "Je bent een vriendelijke AI-assistent. "
        "Je antwoordt altijd in het Nederlands. "
        "Je legt moeilijke onderwerpen eenvoudig uit."
    )
)