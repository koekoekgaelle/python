import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY ontbreekt in het .env-bestand.")

chatbot = ChatOpenAI(
    model="gpt-5.6",
)

print("AI-assistent gestart. Typ 'stop' om af te sluiten.\n")

while True:
    vraag = input("Jij: ").strip()

    if vraag.lower() == "stop":
        print("Assistent: Tot ziens!")
        break

    if not vraag:
        continue

    try:
        antwoord = chatbot.invoke(vraag)
        print(f"\nAssistent: {antwoord.content}\n")
    except Exception as fout:
        print(f"\nEr ging iets mis: {fout}\n")