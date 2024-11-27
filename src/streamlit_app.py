"""Advanced Analytics scavenger hunt application."""

import re
import time

from streamlit_geolocation import streamlit_geolocation
from geopy.distance import geodesic
import streamlit as st

from models import State, Game
from helpers import calculate_bearing, log_ndjson, handle_question
from constants import STATE_FILE, GAME_FILE, LOGGING_FILE


# Get game files
game = Game.from_yaml_file(file_path=GAME_FILE)
state = State.from_yaml_file(file_path=STATE_FILE, game=game)


#############
# Scavenger #
#############
def scavenger(team_name: str) -> None:
    """Application for the scavenger hunt."""
    team_state = state.get_or_create_team_state(
        team_name=team_name,
    )

    ## Title
    title_column_1, title_column_2 = st.columns([5, 1], vertical_alignment="bottom")
    with title_column_1:
        st.title("Scavenger hunt 🕵")
    with title_column_2:
        if st.button(label="Reload"):  # pragma: no cover
            st.rerun()

    ## Top section
    if len(team_state.solved) == 0:
        st.write(
            "Welcome to the Advanced Analytics scavenger hunt! Your goal is to find the hidden locations and answer the questions to score points. Questions will only be revealed when you are within a certain distance of the goal location. When a question is answered correctly, the next location will be the closest one. When answered incorrectly, the next location will be the farthest one. Answer wisely!"
        )

    st.markdown("---")
    st.markdown(f"**Playing as team  :** {team_name}")
    st.markdown(f"**Solved locations :** {len(team_state.solved)} / {len(game.locations)}")
    st.write("Press button to get current location  :")
    location = streamlit_geolocation()

    ## Current goal location
    goal_location = game.get_location_by_name(team_state.goal_location_name)

    # If beam to location is enabled show button
    if state.button_beam_to_location_visible and st.checkbox(label="Beam me to goal location"):
        location = {
            "latitude": goal_location.latitude,
            "longitude": goal_location.longitude,
        }

    distance = None

    ## Check if all locations are solved
    if len(team_state.solved) == len(game.locations):
        st.markdown("---")
        st.success(
            "Congratulations! You have found all the locations and answered all the questions. You are a true scavenger hunt master!"
        )
        return

    ## Location information
    if location is not None and location.get("latitude") is not None:
        # Log location
        log_ndjson(
            file_path=LOGGING_FILE,
            team_name=team_name,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
            solved=len(team_state.solved),
            current_goal=team_state.goal_location_name,
            beam_to_location=state.button_beam_to_location_visible,
        )
        st.markdown("---")
        st.subheader("Location and direction")

        current_location = (location.get("latitude"), location.get("longitude"))
        goal_coordinates = (goal_location.latitude, goal_location.longitude)

        distance = geodesic(current_location, goal_coordinates).meters
        bearing = calculate_bearing(current_location, goal_coordinates)

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
        handle_question(
            goal_location=goal_location,
            team_state=team_state,
            game=game,
        )
    else:
        st.subheader("Question")
        st.write(
            f"You need to be within {game.radius} meters of the goal location to see the question."
        )


def login_page() -> None:
    """Login page for the scavenger hunt."""
    st.title("Team login")

    def update_team_name(team_name: str) -> None:
        """Update team name in session state."""
        if team_name and re.match("^[A-Za-z]+$", team_name):
            st.session_state.team_name = team_name
        else:
            st.error(
                "Team name can only contain uppercase and lowercase letters. No numbers, spaces, or special characters."
            )

    team_name = st.text_input(
        label="Enter your team name (only letters allowed):",
    )
    st.button(
        label="Access Team Page",
        on_click=lambda: update_team_name(team_name),
    )


########
# Main #
########
if "team_name" not in st.session_state:
    login_page()
else:
    scavenger(st.session_state.team_name)
