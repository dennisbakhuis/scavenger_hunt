"""Advanced Analytics scavenger hunt application."""
from pathlib import Path

import streamlit as st

from models import State, Game


STATE_FILE = "data/application_state.yaml"
GAME_FILE = "data/game.yaml"


# Get game files
game = Game.from_yaml_file(file_path=GAME_FILE)
state = State.from_yaml_file(file_path=STATE_FILE, game=game)

# Reload variables from state
if "index" not in st.session_state:
    st.session_state.index = 0


#############
# Scavenger #
#############
def scavenger_admin():
    """Scavenger hunt admin interface."""
    st.title("Scavenger hunt ADMIN 🕵")
    overview_tab, questions_tab, about_tab = st.tabs(["Overview", "Questions", "About"])

    with overview_tab:
        st.header("Overview")
        st.write(f"Number of registered teams: {state.n_active_teams}")

        st.subheader("Puzzle statistics")
        puzzle_statistics = []
        for ix, location in enumerate(game.locations):
            n_teams_solved = sum(
                1
                for team in state.teams.values()
                if location.name in team.solved
            )
            puzzle_statistics.append({
                "Id": ix + 1,
                "Location": location.name,
                "Teams solved": n_teams_solved,
                "Teams unsolved": state.n_active_teams - n_teams_solved,
            })

        st.dataframe(puzzle_statistics)

        st.subheader("Team statistics")
        team_statistics = []
        for team in state.teams.values():
            team_statistics.append({
                "Team": team.name,
                "Score": sum([score for score in team.solved.values()]),
                "Solved": len(team.solved),
            })

        st.dataframe(team_statistics)

    with questions_tab:

        def previous_item():
            st.session_state.index = (st.session_state.index - 1) % len(game.locations)

        def next_item():
            st.session_state.index = (st.session_state.index + 1) % len(game.locations)

        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("Previous"):
                previous_item()

        with col2:
            if st.button("Next"):
                next_item()

        location = game.locations[st.session_state.index]

        base_question_path = Path(GAME_FILE).parent
        image_file = base_question_path / location.image

        st.subheader(location.name)
        st.markdown(location.description)
        if image_file.exists():
            st.image(str(image_file), use_column_width=True)

        st.subheader("Answer:")
        for option in location.options:
            st.write(f"Option: {option.option}, Score: {option.score}")

    with about_tab:
        st.header("About Us")
        st.write("Here's some information about us.")
        st.bar_chart([10, 20, 30, 40])


########
# Main #
########
scavenger_admin()
