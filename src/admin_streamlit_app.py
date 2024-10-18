"""Advanced Analytics scavenger hunt application."""
import os
import json
from pathlib import Path

import streamlit as st

from models import State, Game


STATE_FILE = "data/application_state.json"
GAME_FILE = "data/game.json"
QUESTION_PATH = "data/questions"


if 'index' not in st.session_state:
    st.session_state.index = 0

def load_game_data():
    with open(GAME_FILE, "r") as file:
        game_data_dict = json.load(file)
        return Game.model_validate(game_data_dict)


def load_application_state() -> State:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as file:
            state_data = json.load(file)
            return State.model_validate(state_data)
    else:
        return State()


#############
# Scavenger #
#############
def scavenger_admin():
    game = load_game_data()
    state = load_application_state()

    st.title("Scavenger hunt ADMIN 🕵")
    overview_tab, questions_tab, about_tab = st.tabs(["Overview", "Questions", "About"])

    with overview_tab:
        st.header("Overview")
        st.write(f"Number of active teams: {state.n_active_teams}")

        for location in game.locations:
            n_teams_solved = sum(1 for team in state.teams.values() if team.goal_location_name.name == location.name)
            st.write(f"Location: {location.name}, Solved by {n_teams_solved} teams")

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

        description_file = Path(f"{QUESTION_PATH}/{location.description_file}")
        image_file = description_file.parent / f"{description_file.stem}.png"

        if description_file.exists():
            with open(f"{QUESTION_PATH}/{location.description_file}", "r") as file:
                st.markdown(file.read())
            if image_file.exists():
                st.image(str(image_file), use_column_width=True)
        else:
            st.subheader("Question")
            st.write(f"Question: {location.question}")
            
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