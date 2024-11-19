"""Integration test for the admin Streamlit app."""
import tempfile
import json
import yaml
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from models import Game
import constants


STREAMLIT_APP_FILE = "src/admin_streamlit_app.py"


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


def test_admin_streamlit_app():
    """Test if streamlit app starts."""
    at = AppTest.from_file(STREAMLIT_APP_FILE)
    at.run()
    assert not at.exception

    # test if app is loading
    assert at.title[0].value == "Scavenger hunt admin 🕵"


def test_streamlit_overview_tab():
    """Test if streamlit app starts."""
    at = AppTest.from_file(STREAMLIT_APP_FILE)

    data = """\
button_beam_to_location_visible: false
teams:
  Team:
    goal_location_name: Three switches, three bulbs
    name: Dennis
    solved:
      Three doors: 1
      Three switches, three bulbs: 1
  Dennis:
    goal_location_name: A wolf, a goat, and a cabbage
    name: Johanna
    solved:
      A wolf, a goat, and a cabbage: -1
      Bridge Crossing: 2
"""
    with open(constants.STATE_FILE, "w") as f:
        f.write(f"{data}\n")

    at.run()
    assert not at.exception

    # test if Overview are showing
    assert at.markdown[0].value == "Number of registered teams: 2"

    # change beam_to_location to True
    at.checkbox[0].check().run()

    with open(constants.STATE_FILE, "r") as f:
        data = yaml.safe_load(f)

    assert data["button_beam_to_location_visible"]

    # test delete data
    at.checkbox[1].check().run()
    at.button[1].click().run()

    assert not Path(constants.STATE_FILE).exists()
    assert not Path(constants.LOGGING_FILE).exists()


def test_admin_streamlit_statistics_tab():
    """Test if streamlit app starts."""
    at = AppTest.from_file(STREAMLIT_APP_FILE)

    team_data = [
        {"team_name": "Team", "timestamp": "2024-11-19 14:16:10", "latitude": 50.36217626641079, "longitude": 7.604774011633124, "solved": 0, "current_goal": "Three switches, three bulbs", "beam_to_location": True},
        {"team_name": "Johanna", "timestamp": "2024-11-19 15:39:45", "latitude": 50.35992338937352, "longitude": 7.600863034946477, "solved": 0, "current_goal": "Weighing Coins", "beam_to_location": True},
    ]

    with open(constants.LOGGING_FILE, "w") as file:
        for data in team_data:
            file.write(f"{json.dumps(data)}\n")

    at.run()
    assert not at.exception

    # test if Stats are showing
    assert at.subheader[-1].value == "Summary statistics"


def test_admin_streamlit_questions_tab(game):
    """Test if streamlit app starts."""
    at = AppTest.from_file(STREAMLIT_APP_FILE)
    at.session_state["index"] = 0

    at.run()
    assert not at.exception

    # test if at is at questions tab
    assert at.subheader[3].value == f"1 - {game.locations[0].name}"

    # by default should not show the score
    assert not at.checkbox[2].value
    for item in at.markdown:
        if item.value.startswith("Option:"):
            assert "Score" not in item.value

    # show the score
    at.checkbox[2].check().run()
    for item in at.markdown:
        if item.value.startswith("Option:"):
            assert "Score" in item.value

    # test going to next question/location
    for ix in range(1, len(game.locations)):
        at.button[2].click().run()
        assert at.session_state["index"] == ix
        assert at.subheader[3].value == f"{ix + 1} - {game.locations[ix].name}"

    # one more click should go back to the first question
    at.button[2].click().run()
    assert at.session_state["index"] == 0
    assert at.subheader[3].value == f"1 - {game.locations[0].name}"

    # test going to previous question/location
    at.button[1].click().run()
    assert at.session_state["index"] == len(game.locations) - 1
    assert at.subheader[3].value == f"{len(game.locations)} - {game.locations[-1].name}"
