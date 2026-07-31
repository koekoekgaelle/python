from pathlib import Path

SYSTEM_PROMPT = Path(
    r"C:\Users\gaell\My-AI-Assistant\assistant\aiassistant\aisystemmessage.txt"
    ).read_text(encoding="utf-8").strip()
