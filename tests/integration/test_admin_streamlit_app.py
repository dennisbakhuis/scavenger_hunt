"""Integration test for the Streamlit app."""
import tempfile

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


def test_streamlit_app():
    """Test if streamlit app starts."""
    at = AppTest.from_file(STREAMLIT_APP_FILE)
    at.run()
    assert not at.exception

    # test if at is at login page
    assert at.title[0].value == "Scavenger hunt admin 🕵"
