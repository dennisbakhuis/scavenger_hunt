"""Integration test for the Streamlit app."""

import tempfile
import threading
from copy import deepcopy

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


def test_streamlit_load_test_with_m_teams(monkeypatch, game):
    """Load test with M teams playing concurrently using multithreading."""
    M_TEAMS = 10  # Number of teams to simulate
    N_STEPS = 5  # Number of steps to move towards each goal

    team_names = [f"Team{i+1}" for i in range(M_TEAMS)]
    teams_completed = set()
    threads = []

    # Shared resources
    game_copies = {team_name: deepcopy(game) for team_name in team_names}

    # Define a lock for thread-safe print statements
    print_lock = threading.Lock()

    # Function to simulate gameplay for a single team
    def simulate_team(team_name):
        at = AppTest.from_file(STREAMLIT_APP_FILE)
        at.session_state["team_name"] = team_name
        at.session_state["latitude"] = 0
        at.session_state["longitude"] = 0
        at.run()

        # Ensure the team receives the initial message
        assert at.markdown[-1].value.startswith("You need to be within")

        # Patch the location system for this team's session
        def get_coordinates():
            """Return the current coordinates from session state."""
            return {
                "latitude": at.session_state["latitude"],
                "longitude": at.session_state["longitude"],
            }

        # Monkeypatch within the team's thread
        monkeypatch.setattr("streamlit_geolocation.streamlit_geolocation", get_coordinates)

        # Retrieve the game copy for this team
        team_game = game_copies[team_name]

        while True:
            # Retrieve the current state and goal for the team
            state = State.from_yaml_file(
                file_path=constants.STATE_FILE, game=team_game, team_name=team_name
            )
            goal_name = state.teams[team_name].goal_location_name
            goal = team_game.get_location_by_name(goal_name)

            with print_lock:
                print(f"{team_name} is moving towards: {goal_name}")

            # Simulate moving towards the goal in N_STEPS
            start_lat = at.session_state["latitude"]
            start_lon = at.session_state["longitude"]
            delta_lat = (goal.latitude - start_lat) / N_STEPS
            delta_lon = (goal.longitude - start_lon) / N_STEPS

            for _ in range(N_STEPS):
                at.session_state["latitude"] += delta_lat
                at.session_state["longitude"] += delta_lon
                at.run()

                distance = geodesic(
                    (at.session_state["latitude"], at.session_state["longitude"]),
                    (goal.latitude, goal.longitude),
                ).meters

                if distance > team_game.radius:
                    assert at.markdown[-1].value.startswith("You need to be within")
                else:
                    assert at.subheader[-2].value == goal_name

            # Answer the question at the goal location
            if goal.question_type == QuestionType.MultipleChoice:
                at.button[1].click().run()  # Click the first choice
            elif goal.question_type == QuestionType.OpenQuestion:
                at.text_input[0].input("Answer").run()
                at.button[1].click().run()  # Submit the answer

            # Check if the team has completed all locations
            state = State.from_yaml_file(
                file_path=constants.STATE_FILE, game=team_game, team_name=team_name
            )
            if state.teams[team_name].completed:
                assert at.success[0].value == (
                    "Congratulations! You have found all the locations and answered all the questions. "
                    "You are a true scavenger hunt master!"
                )
                with print_lock:
                    print(f"{team_name} has completed the game!")
                teams_completed.add(team_name)
                break

    # Start a thread for each team
    for team_name in team_names:
        thread = threading.Thread(target=simulate_team, args=(team_name,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    assert len(teams_completed) == M_TEAMS
    print("All teams have completed the game concurrently!")
