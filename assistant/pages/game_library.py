import re

import streamlit as st

from assistant.embedding_and_db.document_service import process_pdf
from assistant.repositories.game_repository import (
    create_game,
    get_all_games,
)


# TODO (RensBlitz): deze make_slug() doet hetzelfde als create_slug() in
# assistant/utils/text.py, alleen zonder de unicode-normalisatie (dus "café"
# wordt hier niet netjes "cafe"). We gebruiken nu deze losse versie en
# create_slug() in utils/text.py wordt nergens meer aangeroepen. Dit is
# belangrijk om op te ruimen: gebruik overal create_slug() uit utils/text.py
# en verwijder deze duplicate functie hier, anders lopen de twee implementaties
# ooit uit elkaar en krijg je inconsistente slugs.
def make_slug(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def show_game_library():
    st.title("📚 Game Library")
    st.write("Kies een bestaand spel of upload een nieuw spel.")

    games = get_all_games()

    for game in games:
        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(f"### 🎲 {game['name']}")

        with col2:
            if st.button(
                "Openen",
                key=f"open_game_{game['id']}",
            ):
                # TODO (RensBlitz): hier zetten we "game_id" en "game_name" in
                # session_state, maar app.py (initialize_session_state) kent
                # alleen "current_game_id", "current_session_id" en "messages".
                # Dit zijn dus 2 losse naamgevingen voor hetzelfde concept, en
                # deze waarden hier worden verderop nooit gelezen. Dit is
                # belangrijk om te fixen, want dit is een bug in wording: trek
                # dit gelijk met de keys uit app.py zodat er 1 duidelijke bron
                # van waarheid is voor de session-state.
                st.session_state.game_id = int(game["id"])
                st.session_state.game_name = game["name"]
                st.session_state.page = "session"
                st.rerun()

    st.divider()

    with st.expander("➕ Mijn spel staat er niet bij"):
        game_name = st.text_input("Naam van het spel")

        uploaded_file = st.file_uploader(
            "Upload de PDF-handleiding",
            type=["pdf"],
        )

        if st.button("Spel toevoegen"):
            if not game_name.strip():
                st.error("Vul een spelnaam in.")

            elif uploaded_file is None:
                st.error("Upload eerst een PDF.")

            else:
                try:
                    with st.spinner("Spel aan het toevoegen..."):
                        slug = make_slug(game_name)

                        game = create_game(
                            name=game_name.strip(),
                            slug=slug,
                        )

                        game_id =int(game["id"])

                        result = process_pdf(
                            uploaded_file=uploaded_file,
                            game_id=game_id,
                            language="nl",
                            document_type="rulebook",
                        )

                

                    st.session_state.game_id = game_id
                    st.session_state.game_name = game["name"]
                    st.session_state.page = "session"

                    st.success(f"{game['name']} is toegevoegd.")
                    st.rerun()
                except Exception as error:
                    st.error(f"Fout bij het toevoegen van het spel: {error}")