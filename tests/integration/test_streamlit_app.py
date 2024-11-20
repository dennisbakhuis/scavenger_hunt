"""Integration test for the Streamlit app."""

import tempfile
from pathlib import Path

import pytest
from geopy.distance import geodesic
from streamlit.testing.v1 import AppTest

from models import State, Game, QuestionType
import constants


STREAMLIT_APP_FILE = "src/streamlit_app.py"


@pytest.fixture(autouse=True)
def temporary_state_folder():
    """Create temporary state folder for the state file."""
    previous_state_file = constants.STATE_FILE
    previous_log_file = constants.LOGGING_FILE

    with tempfile.TemporaryDirectory() as temporary_folder:
        constants.STATE_FILE = f"{temporary_folder}/state.yaml"
        constants.LOGGING_FILE = f"{temporary_folder}/logging.ndjson"
        yield

    constants.STATE_FILE = previous_state_file
    constants.LOGGING_FILE = previous_log_file


@pytest.fixture
def game():
    """Get game object."""
    return Game.from_yaml_file(file_path=constants.GAME_FILE)


def test_streamlit_app():
    """Test if streamlit app starts."""
    at = AppTest.from_file(STREAMLIT_APP_FILE)
    at.run()
    assert not at.exception

    # test if at is at login page
    assert at.title[0].value == "Team login"


def test_streamlit_fill_team_name_wrong_characters():
    """Test fill in invalid team name."""
    at = AppTest.from_file(STREAMLIT_APP_FILE)
    at.run()

    # Fill in team name with spaces
    for wrong_name in [
        "",
        " ",
        "Team 1",
        "Team$",
        "Team1!",
        "#",
    ]:
        at.text_input[0].input(wrong_name).run()
        at.button[0].click().run()
        assert at.error[0].value.startswith(
            "Team name can only contain uppercase and lowercase letters."
        )


def test_streamlit_valid_team_name(game):
    """Test fill in valid team name."""
    at = AppTest.from_file(STREAMLIT_APP_FILE)
    at.run()

    # Fill in team name with valid name
    at.text_input[0].input("Team").run()
    at.button[0].click().run()

    assert at.title[0].value == "Scavenger hunt 🕵"
    assert at.session_state["team_name"] == "Team"
    assert at.columns[3].markdown[0].value == ": Team"

    # Check if the team name is stored in the session state
    state_file = Path(constants.STATE_FILE)
    assert state_file.exists()

    state = State.from_yaml_file(file_path=constants.STATE_FILE, game=game)
    assert state.teams["Team"].name == "Team"


def test_streamlit_button_beam_to_location(game):
    """Test the beam to location button."""
    at = AppTest.from_file(STREAMLIT_APP_FILE)
    at.session_state["team_name"] = "Team"
    at.run()

    # By default, the button should not be visible
    assert len(at.checkbox) == 0

    # Set option for button visibility to True
    state = State.from_yaml_file(file_path=constants.STATE_FILE, game=game)
    state.button_beam_to_location_visible = True
    state.save()
    at.run()

    assert at.checkbox[0].label == "Beam me to goal location"
    assert not at.checkbox[0].value
    assert at.markdown[-1].value.startswith("You need to be within")

    # Turn checkbox on and check if beamed to location
    at.checkbox[0].check().run()
    goal_name = state.teams["Team"].goal_location_name

    assert at.subheader[-2].value == goal_name


def test_streamlit_normal_run_with_steps(monkeypatch, game):
    """Test for a single user to go through all the stations with incremental GPS updates."""
    N_STEPS = 5

    at = AppTest.from_file(STREAMLIT_APP_FILE)
    at.session_state["team_name"] = "Team"
    at.run()

    # Not yet at question location
    assert at.markdown[-1].value.startswith("You need to be within")

    # Patch location system
    global latitude, longitude
    latitude, longitude = 0, 0

    def get_coordinates():
        """Map coordinates for the current location."""
        return {
            "latitude": latitude,
            "longitude": longitude,
        }

    monkeypatch.setattr("streamlit_geolocation.streamlit_geolocation", get_coordinates)

    # Iterate through stations
    for ix in range(len(game.locations)):
        state = State.from_yaml_file(file_path=constants.STATE_FILE, game=game)
        goal_name = state.teams["Team"].goal_location_name
        goal = game.get_location_by_name(goal_name)

        print(f"Goal {ix+1:<2}: {goal_name}")

        # Simulate moving towards the goal in n_steps
        start_latitude, start_longitude = latitude, longitude
        delta_lat = (goal.latitude - start_latitude) / N_STEPS
        delta_lon = (goal.longitude - start_longitude) / N_STEPS

        for _ in range(N_STEPS):
            latitude += delta_lat
            longitude += delta_lon
            at.run()

            distance = geodesic(
                (latitude, longitude),
                (goal.latitude, goal.longitude),
            ).meters

            if distance > game.radius:
                assert at.markdown[-1].value.startswith("You need to be within")
            else:
                assert at.subheader[-2].value == goal_name

        # Answer the question
        if goal.question_type == QuestionType.MultipleChoice:
            at.button[1].click().run()  # Click the first button
        elif goal.question_type == QuestionType.OpenQuestion:
            at.text_input[0].input("Answer").run()  # Fill in the answer
            at.button[1].click().run()  # Submit the answer

    # Check if all locations are solved
    assert at.success[0].value == (
        "Congratulations! You have found all the locations and answered all the questions. "
        "You are a true scavenger hunt master!"
    )
