
import streamlit as st

from assistant.embedding_and_db.document_service import process_pdf
from assistant.utils.text import create_slug
from assistant.utils.exceptions import GameCreationError
from assistant.repositories.game_repository import (
    create_game,
    get_all_games,
)



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
                st.session_state.current_game_id = int(game["id"])
                st.session_state.current_game_name = game["name"]
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
            cleaned_game_name = game_name.strip()


            if not cleaned_game_name:
                st.error("Vul een spelnaam in.")
                return

            if uploaded_file is None:
                st.error("Upload eerst een PDF.")
                return

            try:
                with st.spinner("Spel aan het toevoegen..."):
                    slug = create_slug(cleaned_game_name)

                    game = create_game(
                        name=cleaned_game_name,
                        slug=slug,
                    )

                    game_id = int(game["id"])

                    process_pdf(
                        uploaded_file=uploaded_file,
                        game_id=game_id,
                        language="nl",
                        document_type="rulebook",
                    )

                st.session_state.current_game_id = game_id
                st.session_state.current_game_name = game["name"]
                st.session_state.page = "session"

                st.success(f"{game['name']} is toegevoegd.")
                st.rerun()

            except GameCreationError:
                st.error("Het spel kon niet worden toegevoegd.")
