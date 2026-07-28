import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY ontbreekt in het .env-bestand.")


chatbot = ChatOpenAI(
    model="gpt-5.6",
)

gesprek = [
    SystemMessage(
        content=(
            "Je bent een vriendelijke AI-assistent. "
            "Je antwoordt in het Nederlands en legt dingen duidelijk uit."
        )
    )
]

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
        antwoord = chatbot.invoke(gesprek)

        print(f"\nAssistent: {antwoord.content}\n")

        gesprek.append(AIMessage(content=antwoord.content))

    except Exception as fout:
        print(f"\nEr ging iets mis: {fout}\n")

        # Verwijder de laatste vraag wanneer de API-aanroep mislukt.
        gesprek.pop()