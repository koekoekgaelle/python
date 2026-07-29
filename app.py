import streamlit as st

from assistant.aiassistant.question_answering import answer_question
from assistant.database.supabase_client import supabase
from assistant.pages.game_library import show_game_library


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
        st.header("🎲 Spelsessie")
        st.write(f"**Spel:** {selected_game['name']}")

        if st.session_state.current_session_id is None:
            st.info("Er is nog geen actieve spelsessie.")

            if st.button(
                "Nieuwe spelsessie starten",
                type="primary",
                use_container_width=True,
            ):
                try:
                    start_new_session(selected_game["id"])
                    st.rerun()
                except Exception as exc:
                    st.error(f"Spelsessie starten mislukt: {exc}")

            return

        st.success(
            f"Spel is bezig"
        )

        if st.button(
            "Nieuwe sessie starten",
            use_container_width=True,
        ):
            try:
                start_new_session(selected_game["id"])
                st.rerun()
            except Exception as exc:
                st.error(f"Nieuwe sessie starten mislukt: {exc}")

        st.divider()
        st.subheader("🏆 Scorebord")

        try:
            players = get_session_players(
                st.session_state.current_session_id
            )
        except Exception as exc:
            st.error(f"Spelers ophalen mislukt: {exc}")
            players = []

        if not players:
            st.caption(
                "Nog geen spelers toegevoegd. Typ bijvoorbeeld: "
                "'Voeg Anna en Simon toe.'"
            )
            return

        sorted_players = sorted(
            players,
            key=lambda player: player.get("current_score", 0),
            reverse=True,
        )

        medals = ["🥇", "🥈", "🥉"]

        for index, player in enumerate(sorted_players):
            name = player["name"]
            score = player.get("current_score", 0)

            prefix = medals[index] if index < len(medals) else f"{index + 1}."

            left_column, right_column = st.columns([3, 1])

            with left_column:
                st.write(f"{prefix} **{name}**")

            with right_column:
                st.write(f"**{score}**")


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

    except Exception as exc:
        error_message = f"Er ging iets mis: {exc}"

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
    except Exception as exc:
        st.error(f"Spellen ophalen uit Supabase mislukt: {exc}")
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
