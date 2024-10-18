"""Advanced Analytics scavenger hunt application."""
import re
from pathlib import Path

from streamlit_geolocation import streamlit_geolocation
from streamlit_server_state import server_state, server_state_lock
from geopy.distance import geodesic
import streamlit as st

from models import State, Game
from helpers import calculate_bearing, determine_next_location


STATE_FILE = "data/application_state.json"
GAME_FILE = "data/game.json"
QUESTION_PATH = "data/questions"


# Get game files
game = Game.from_yaml_file(GAME_FILE)
with server_state_lock["state"]:
    if "state" not in server_state:
        server_state.state = State.from_yaml_file(
            file_path=STATE_FILE,
            game=game,
        )

    state = server_state.state


#############
# Scavenger #
#############
def scavenger(team_name):
    """Application for the scavenger hunt."""
    team_state = state.get_or_create_team(
        team_name=team_name,
    )

    ## Top section
    ## - Team name and small description if first location (sovled = 0)
    st.title("Scavenger hunt 🕵")
    if len(team_state.solved) == 0:
        st.write("Welcome to the Advanced Analytics scavenger hunt! Your goal is to find the hidden locations and answer the questions to score points. Questions will only be revealed when you are within a certain distance of the goal location. When a question is answered correctly, the next location will be the closest one. When answered incorrectly, the next location will be the farthest one. Answer wisely!")

    top_column_1, top_column_2 = st.columns([1, 1])
    with top_column_1:
        st.write("Playing as team")
        st.write("Solved locations")
        st.write("Press button to get current location:")
    with top_column_2:
        st.write(f": {team_name}")
        st.write(f": {len(team_state.solved)} / {len(game.locations)}")
        location = streamlit_geolocation()

    distance = None

    ## Check if all locations are solved
    if len(team_state.solved) == len(game.locations):
        st.markdown("---")
        st.success("Congratulations! You have found all the locations and answered all the questions. You are a true scavenger hunt master!")
        return

    ## Location information
    if location is not None and location.get("latitude") is not None:
        st.markdown("---")
        st.subheader("Location and direction")

        current_location = (location.get("latitude"), location.get("longitude"))
        goal_location = (team_state.goal.latitude, team_state.goal.longitude)

        distance = geodesic(current_location, goal_location).meters
        bearing = calculate_bearing(current_location, goal_location)

        location_column_1, location_column_2 = st.columns([1, 1])
        with location_column_1:
            st.write("Current location")
            st.write("Distance to current goal")
            st.write("Direction to current goal")
        with location_column_2:
            st.write(f": {location.get("latitude")}, {location.get("longitude")}")
            st.write(f": {round(distance)} meters")
            st.write(f": {round(bearing)} degrees")


    ## Question when in radius
    st.markdown("---")
    if distance is not None and distance <= game.radius:

        description_file = Path(f"{QUESTION_PATH}/{team_state.goal.description_file}")
        image_file = description_file.parent / f"{description_file.stem}.png"

        if description_file.exists():
            with open(f"{QUESTION_PATH}/{team_state.goal.description_file}", "r") as file:
                st.markdown(file.read())
            if image_file.exists():
                st.image(str(image_file), use_column_width=True)
        else:
            st.subheader("Question")
            st.write(f"Question: {team_state.goal.question}")

        st.subheader("Answer:")
        for option in team_state.goal.options:
            if st.button(option.option):
                team_state.solved[team_state.goal.name] = option.score

                if len(game.locations) - len(team_state.solved) > 0:
                    team_state.goal = determine_next_location(
                        team_state=team_state,
                        game=game,
                        previous_score=option.score,
                        current_location=current_location,
                    )

                state.update_team(team_name, team_state)
                st.rerun()
    else:
        st.subheader("Question")
        st.write(f"You need to be within {game.radius} meters of the goal location to see the question.")


##############
# Login page #
##############
def login_page():
    """Login page for the scavenger hunt."""
    st.title("Team Login")

    team_name = st.text_input("Enter your team name (only letters allowed):")

    if team_name and not re.match("^[A-Za-z]+$", team_name):
        st.error("Team name can only contain uppercase and lowercase letters. No numbers, spaces, or special characters.")
    elif st.button("Access Team Page") and team_name:
        st.session_state.team_name = team_name
        st.rerun()


########
# Main #
########
if "team_name" not in st.session_state:
    login_page()
else:
    scavenger(st.session_state.team_name)
