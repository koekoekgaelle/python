import re

import streamlit as st

from assistant.embedding_and_db.document_service import process_pdf
from assistant.repositories.game_repository import (
    create_game,
    get_all_games,
)


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