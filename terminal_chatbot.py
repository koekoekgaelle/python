import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from assistant.aiassistant.chatbot import create_chatbot

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY ontbreekt in het .env-bestand.")

agent = create_chatbot()
gesprek = []

print("AI-assistent gestart. Typ 'stop' om af te sluiten.\n")

while True:
    vraag = input("Jij: ").strip()

    if vraag.lower() == "stop":
        print("Assistent: Tot ziens!")
        break

    if not vraag:
        continue

    gesprek.append(HumanMessage(content=vraag))

    try:
        resultaat = agent.invoke(
            {
                "messages": gesprek,
            }
        )

        gesprek = resultaat["messages"]
        laatste_bericht = gesprek[-1]

        print(f"\nAssistent: {laatste_bericht.content}\n")

    except Exception as fout:
        print(f"\nEr ging iets mis: {fout}\n")
        gesprek.pop()