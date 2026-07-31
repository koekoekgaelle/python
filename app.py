from dbm import sqlite3

import streamlit as st

from assistant.aiassistant.question_answering import answer_question
from assistant.embedding_and_db.supabase_client import supabase
from assistant.pages.game_library import show_game_library
from typing import Any

import requests


st.set_page_config(
    page_title="AI Board Game Assistant",
    page_icon="🎲",
    layout="wide",
)

if "page" not in st.session_state:
    st.session_state.page = "session"


def initialize_session_state() -> None:
    defaults = {
        "current_session_id": None,
        "current_game_id": None,
        "messages": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_games() -> list[dict]:
    response = (
        supabase.table("games")
        .select("id, name")
        .order("name")
        .execute()
    )

    return response.data or []


def create_game_session(game_id: int) -> dict:
    response = (
        supabase.table("game_sessions")
        .insert(
            {
                "game_id": game_id,
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError("De spelsessie kon niet worden aangemaakt.")

    return response.data[0]


def get_session_players(session_id: int) -> list[dict]:
    response = (
        supabase.table("session_players")
        .select("id, name, current_score")
        .eq("session_id", session_id)
        .order("id")
        .execute()
    )

    return response.data or []


def start_new_session(game_id: int) -> None:
    session = create_game_session(game_id)

    st.session_state.current_session_id = session["id"]
    st.session_state.current_game_id = game_id
    st.session_state.messages = []


def reset_session_when_game_changes(game_id: int) -> None:
    if st.session_state.current_game_id != game_id:
        st.session_state.current_session_id = None
        st.session_state.current_game_id = game_id
        st.session_state.messages = []


def render_sidebar(selected_game: dict) -> None:
    with st.sidebar:
        if st.button("🎲 Alle games / game toevoegen", use_container_width=True):
            st.session_state.page = "library"
            st.rerun()

    if st.session_state.page == "library":
        show_game_library()
        st.stop()

    with st.sidebar:
        render_session_header(selected_game)

        if st.session_state.current_session_id is None:
            render_inactive_session(selected_game["id"])
            return

        render_active_session(selected_game["id"])
        render_scoreboard(st.session_state.current_session_id)


def render_library_button() -> None:
    """Render de knop waarmee de gebruiker teruggaat naar de gamebibliotheek."""
    with st.sidebar:
        if st.button(
            "🎲 Alle games / game toevoegen",
            use_container_width=True,
        ):
            st.session_state.page = "library"
            st.rerun()


def render_session_header(selected_game: dict[str, Any]) -> None:
    """Render algemene informatie over de geselecteerde game."""
    st.header("🎲 Spelsessie")
    st.write(f"**Spel:** {selected_game['name']}")


def render_inactive_session(game_id: int) -> None:
    """Render de UI wanneer er nog geen actieve sessie is."""
    st.info("Er is nog geen actieve spelsessie.")

    render_new_session_button(
        game_id=game_id,
        label="Nieuwe spelsessie starten",
        primary=True,
    )


def render_active_session(game_id: int) -> None:
    """Render de bediening voor een actieve sessie."""
    st.success("Spel is bezig")

    render_new_session_button(
        game_id=game_id,
        label="Nieuwe sessie starten",
    )


def render_new_session_button(
    game_id: int,
    label: str,
    *,
    primary: bool = False,
) -> None:
    """Render een knop waarmee een nieuwe spelsessie wordt gestart."""
    if not st.button(
        label,
        type="primary" if primary else "secondary",
        use_container_width=True,
    ):
        return

    try:
        start_new_session(game_id)
        st.rerun()
    except requests.RequestException:
        st.error("Kan geen verbinding maken met de server. Controleer je internetverbinding.")
    except ValueError:
        st.error("Ongeldige gegevens ontvangen.")

def render_scoreboard(session_id: int) -> None:
    """Haal spelers op en render het scorebord."""
    st.divider()
    st.subheader("🏆 Scorebord")

    players = load_session_players(session_id)

    if players is None:
        # Er is al een foutmelding getoond.
        return

    if not players:
        render_empty_scoreboard()
        return

    sorted_players = sorted(
        players,
        key=lambda player: player.get("current_score", 0),
        reverse=True,
    )

    for position, player in enumerate(sorted_players, start=1):
        render_scoreboard_row(player, position)


def load_session_players(
    session_id: int,
) -> list[dict[str, Any]] | None:
    """Haal spelers op en handel fouten op één centrale plek af."""
    try:
        players = get_session_players(session_id)
    except sqlite3.Error:
        st.error(
            "Er ging iets mis bij het ophalen van de spelers. "
            "Probeer het later opnieuw."
        )
        


def render_empty_scoreboard() -> None:
    """Render de melding voor een scorebord zonder spelers."""
    st.caption(
        "Nog geen spelers toegevoegd. Typ bijvoorbeeld: "
        "'Voeg Anna en Simon toe.'"
    )


def render_scoreboard_row(
    player: dict[str, Any],
    position: int,
) -> None:
    """Render één speler op het scorebord."""
    name = player.get("name", "Onbekende speler")
    score = player.get("current_score", 0)
    prefix = get_position_prefix(position)

    left_column, right_column = st.columns([3, 1])

    with left_column:
        st.write(f"{prefix} **{name}**")

    with right_column:
        st.write(f"**{score}**")


def get_position_prefix(position: int) -> str:
    """Geef een medaille of positienummer terug."""
    if position <= len(MEDALS):
        return MEDALS[position - 1]

    return f"{position}."


def render_chat_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_question(
    question: str,
    selected_game: dict,
) -> None:
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
            with st.spinner("Even nadenken..."):
                result = answer_question(
                    question=question,
                    game_id=selected_game["id"],
                    session_id=st.session_state.current_session_id,
                )

            answer = result["answer"]
            st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    except Exception:
        error_message = ("Er is iets misgegaan")

        with st.chat_message("assistant"):
            st.error(error_message)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_message,
            }
        )


def main() -> None:
    initialize_session_state()

    st.title("🎲 AI Board Game Assistant")
    st.caption(
        "Stel regelvragen, voeg spelers toe en houd scores bij."
    )

    try:
        games = get_games()
    except Exception:
        st.error( "Spellen ophalen mislukt. Controleer je internetverbinding of probeer het later opnieuw.")
        st.stop()

    if not games:
        st.warning(
            "Er staan nog geen spellen in de tabel 'games'."
        )
        st.stop()

    selected_game = st.selectbox(
        "Kies een bordspel",
        options=games,
        format_func=lambda game: game["name"],
    )

    reset_session_when_game_changes(selected_game["id"])
    render_sidebar(selected_game)

    st.subheader(selected_game["name"])

    if st.session_state.current_session_id is None:
        st.info(
            "Start eerst een spelsessie via de zijbalk."
        )
        st.stop()

    render_chat_history()

    question = st.chat_input(
         "Stel een regelvraag of geef een score door..."
    )

    if question:
        handle_question(
            question=question,
            selected_game=selected_game,
        )

        st.rerun()


if __name__ == "__main__":
    main()
