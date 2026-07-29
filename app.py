import os
import re
import unicodedata

import streamlit as st
from dotenv import load_dotenv

from assistant.aiassistant.question_answering import answer_question
from assistant.embedding.document_service import process_pdf
from assistant.repositories.game_repository import (
    create_game,
    get_all_games,
    get_game_by_slug,
)


# =========================
# Configuratie
# =========================

load_dotenv()

st.set_page_config(
    page_title="AI Board Game Assistant",
    page_icon="🎲",
    layout="centered",
)

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY ontbreekt in het .env-bestand.")
    st.stop()


# =========================
# Hulpfuncties
# =========================

def create_slug(text: str) -> str:
    """
    Zet een spelnaam om naar een URL-vriendelijke slug.

    Voorbeeld:
    'Ticket to Ride' -> 'ticket-to-ride'
    """

    normalized_text = unicodedata.normalize("NFKD", text)
    ascii_text = normalized_text.encode("ascii", "ignore").decode("ascii")
    lowercase_text = ascii_text.lower()

    slug = re.sub(r"[^a-z0-9]+", "-", lowercase_text)
    slug = re.sub(r"-+", "-", slug)

    return slug.strip("-")


def clean_text(text: str) -> str:
    """
    Verwijder overbodige enters en meerdere spaties.
    """

    return " ".join(text.split())


def show_sources(sources: list[dict]) -> None:
    """
    Toon de gebruikte fragmenten uit de handleiding.
    """

    if not sources:
        return

    with st.expander("📚 Bekijk gebruikte bronnen"):
        for index, source in enumerate(sources, start=1):
            page_number = source.get("page_number", "Onbekend")
            chunk_number = source.get("chunk_number", "Onbekend")
            similarity = source.get("similarity") or 0
            content = clean_text(source.get("content", ""))

            st.markdown(
                f"**Bron {index} — pagina {page_number}, "
                f"fragment {chunk_number}**"
            )

            st.caption(f"Similarity: {similarity:.4f}")
            st.write(content)
            st.divider()


def show_missing_game_form() -> None:
    """
    Toon het formulier waarmee een nieuw spel en een PDF-handleiding
    kunnen worden toegevoegd.
    """

    st.subheader("➕ Nieuw spel toevoegen")

    st.info(
        "Dit spel staat nog niet in onze database. "
        "Wil je helpen de database uit te breiden? "
        "Vul de naam in en upload de PDF-handleiding."
    )

    with st.form("add_game_form", clear_on_submit=False):
        game_name = st.text_input(
            "Naam van het spel",
            placeholder="Bijvoorbeeld: Ticket to Ride",
        )

        selected_language = st.selectbox(
            "Taal van de handleiding",
            options=["nl", "en", "de", "fr"],
            format_func=lambda language: {
                "nl": "Nederlands",
                "en": "Engels",
                "de": "Duits",
                "fr": "Frans",
            }[language],
        )

        uploaded_file = st.file_uploader(
            "PDF-handleiding",
            type=["pdf"],
            help="Upload de spelregels als PDF-bestand.",
        )

        submitted = st.form_submit_button(
            "Spel en handleiding toevoegen",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    clean_game_name = game_name.strip()

    if not clean_game_name:
        st.warning("Vul eerst de naam van het spel in.")
        return

    if uploaded_file is None:
        st.warning("Upload eerst een PDF-handleiding.")
        return

    slug = create_slug(clean_game_name)

    if not slug:
        st.error("Van deze spelnaam kon geen geldige slug worden gemaakt.")
        return

    try:
        existing_game = get_game_by_slug(slug)

        if existing_game:
            st.warning(
                f"Het spel '{existing_game['name']}' staat al in de database."
            )
            return

        with st.status(
            "Spel wordt toegevoegd...",
            expanded=True,
        ) as status:
            st.write("1. Spel toevoegen aan de database")

            created_game = create_game(
                name=clean_game_name,
                slug=slug,
            )

            st.write("2. PDF uitlezen")

            import_result = process_pdf(
                uploaded_file=uploaded_file,
                game_id=created_game["id"],
                language=selected_language,
                document_type="rulebook",
            )

            st.write("3. Embeddings maken en fragmenten opslaan")

            status.update(
                label="Spel en handleiding zijn toegevoegd!",
                state="complete",
                expanded=False,
            )

        st.success(
            f"🎉 '{created_game['name']}' is succesvol toegevoegd."
        )

        if import_result:
            with st.expander("Bekijk importdetails"):
                st.write(import_result)

        st.session_state["selected_game_id"] = created_game["id"]
        st.session_state["active_game_id"] = created_game["id"]
        st.session_state["messages"] = []
        st.session_state["flash_message"] = (
            f"🎉 '{created_game['name']}' is toegevoegd. "
            "Je kunt nu meteen een vraag stellen."
        )

        st.rerun()

        if st.button(
            f"Vragen stellen over {created_game['name']}",
            type="primary",
            use_container_width=True,
        ):
            st.rerun()

    except Exception as error:
        st.error(
            "Het spel of de handleiding kon niet worden toegevoegd."
        )
        st.exception(error)


def initialize_chat_state() -> None:
    """
    Initialiseer de chatgeschiedenis.
    """

    if "messages" not in st.session_state:
        st.session_state.messages = []


def clear_chat() -> None:
    """
    Wis de huidige chatgeschiedenis.
    """

    st.session_state.messages = []


# =========================
# Applicatie
# =========================

def main() -> None:
    initialize_chat_state()

    st.title("🎲 AI Board Game Assistant")
    flash_message = st.session_state.pop("flash_message", None)

    if flash_message:
        st.success(flash_message)

    st.write(
        "Kies een bordspel en stel een vraag over de spelregels."
    )

    try:
        games = get_all_games()
    except Exception as error:
        st.error("De spellen konden niet worden opgehaald uit Supabase.")
        st.exception(error)
        return

    game_by_id = {
        game["id"]: game
        for game in games
    }

    game_options = [
        None,
        *game_by_id.keys(),
        "missing",
    ]

    stored_game_id = st.session_state.get("selected_game_id")

    default_index = 0

    if stored_game_id in game_by_id:
        default_index = game_options.index(stored_game_id)

    selected_option = st.selectbox(
        "Welk spel wil je spelen?",
        options=game_options,
        index=default_index,
        format_func=lambda option: (
            "Kies een spel"
            if option is None
            else "Mijn spel staat er niet tussen"
            if option == "missing"
            else game_by_id[option]["name"]
        ),
    )

    if selected_option is None:
        st.info("Kies eerst een spel uit de lijst.")
        return

    if selected_option == "missing":
        show_missing_game_form()
        return

    selected_game = game_by_id[selected_option]

    previous_game_id = st.session_state.get("active_game_id")

    if previous_game_id != selected_game["id"]:
        clear_chat()
        st.session_state.active_game_id = selected_game["id"]

    st.session_state.selected_game_id = selected_game["id"]

    with st.sidebar:
        st.header("🎲 Geselecteerd spel")
        st.write(selected_game["name"])

        if st.button(
            "🗑️ Nieuw gesprek",
            use_container_width=True,
        ):
            clear_chat()
            st.rerun()

        st.divider()

        st.caption(
            "De antwoorden worden gebaseerd op de handleiding "
            "die voor dit spel in de database staat."
        )

    st.success(f"Geselecteerd spel: {selected_game['name']}")

    # =========================
    # Chatgeschiedenis tonen
    # =========================

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                show_sources(message.get("sources", []))

    # =========================
    # Nieuwe vraag
    # =========================

    question = st.chat_input(
        f"Stel een vraag over {selected_game['name']}"
    )

    if not question:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Ik zoek het antwoord in de handleiding..."):
                result = answer_question(
                    question=question,
                    game_id=selected_game["id"],
                    match_count=15,
                )

            answer = result.get(
                "answer",
                "Ik kon geen antwoord genereren.",
            )

            sources = result.get("sources", [])

            st.markdown(answer)
            show_sources(sources)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }
        )

    except Exception as error:
        st.error("Er ging iets mis bij het beantwoorden van de vraag.")
        st.exception(error)


if __name__ == "__main__":
    main()