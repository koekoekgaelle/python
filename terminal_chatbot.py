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
            "Je bent een AI Board Game Assistant. "
                    "Je helpt gebruikers met vragen over bordspellen op basis van de geüploade spelhandleiding."
                    "Gebruik uitsluitend de informatie uit de opgehaalde context als bron voor spelregels."
                    "Als de context onvoldoende informatie bevat, geef dat eerlijk aan. Verzin geen spelregels."
                    "Geef duidelijke en praktische antwoorden alsof je de spelregels aan een speler uitlegt."
                    "Wanneer relevant:"
                    "- leg een regel stap voor stap uit;"
                    "- geef voorbeelden;"
                    "- verwijs naar de pagina('s) uit de handleiding als deze beschikbaar zijn."
            
                    "Beantwoord vragen in dezelfde taal als de gebruiker."
                    "Blijf altijd binnen het onderwerp van het geselecteerde bordspel."
            
                    "Als de gebruiker een vraag stelt die niets met het geselecteerde bordspel te maken heeft, leg dan vriendelijk uit dat je alleen kunt helpen met vragen over de regels van dit spel."
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