from pathlib import Path
from langchain_core.messages import SystemMessage

SYSTEM_PROMPT = SystemMessage(
    content=Path(
        r"C:\Users\gaell\My-AI-Assistant\assistant\aiassistant\aisystemmessage.txt"
    ).read_text(encoding="utf-8").strip()
)