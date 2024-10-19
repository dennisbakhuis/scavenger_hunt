"""Tests for the State model."""
import tempfile
import os
import yaml
from pathlib import Path
from typing import Generator

import pytest
from unittest.mock import MagicMock

from models import State, TeamState, Location, AnswerOption, QuestionType


@pytest.fixture
def game() -> MagicMock:
    """Create a `MagicMock` for the `Game` object for testing."""
    location = Location(
        name="Test Location",
        latitude=0.0,
        longitude=0.0,
        question_type=QuestionType.MultipleChoice,
        question="A test location.",
        answer=[AnswerOption(option="Option A", score=10)],
        image="test_image.png",
    )
    game = MagicMock()
    game.locations = [location]
    return game


@pytest.fixture
def state_file() -> Generator[str, None, None]:
    """Create a temporary file for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield os.path.join(temp_dir, "test_game_state.yaml")


def test_state_creation(state_file, game):
    """Test the creation of the `State` class."""
    state = State(file_path=state_file, game=game)
    assert state.teams == {}
    assert state.n_active_teams == 0


def test_team_exists(state_file, game):
    """Test that the `team_exists` method correctly checks for team existence."""
    state = State(file_path=state_file, game=game)
    assert not state.team_exists("Team1")

    state.teams["Team1"] = TeamState(name="Team1", goal_location_name=game.locations[0].name)
    assert state.team_exists("Team1")


def test_get_team_state(state_file, game):
    """Test the `get_team_state` method to ensure it returns the correct `TeamState`."""
    state = State(file_path=state_file, game=game)
    state.teams["Team1"] = TeamState(name="Team1", goal_location_name=game.locations[0].name)

    assert state.get_team_state("Team1").name == "Team1"

    with pytest.raises(ValueError):
        state.get_team_state("NonExistingTeam")


def test_get_or_create_team(state_file, game):
    """Test the `get_or_create_team` method to ensure teams are created correctly if they do not exist."""
    state = State(file_path=state_file, game=game)

    # Test team creation
    team_state = state.get_or_create_team("Team1")
    assert team_state.name == "Team1"
    assert team_state.goal_location_name == game.locations[0].name
    assert state.teams["Team1"].name == "Team1"

    # Test existing team retrieval
    existing_team_state = state.get_or_create_team("Team1")
    assert existing_team_state == team_state


def test_state_from_yaml(state_file, game):
    """Test the `from_yaml_file` method to ensure a state is loaded correctly from a YAML file."""
    # Test creating a new state when the file does not exist
    if Path(state_file).exists():
        os.remove(state_file)  # Ensure the file does not exist before the test

    state = State.from_yaml_file(state_file, game)
    assert state.teams == {}

    # Test saving the state
    state.teams["Team1"] = TeamState(name="Team1", goal_location_name=game.locations[0].name)
    state.save()

    # Now test loading from an existing file
    loaded_state = State.from_yaml_file(state_file, game)
    assert "Team1" in loaded_state.teams
    assert loaded_state.teams["Team1"].name == "Team1"


def test_save_state(state_file, game):
    """Test the `save` method to ensure the state is correctly saved to a YAML file."""
    state = State(file_path=state_file, game=game)
    state.teams["Team1"] = TeamState(name="Team1", goal_location_name=game.locations[0].name)

    state.save()

    with open(state_file, "r") as file:
        loaded_data = yaml.safe_load(file)
        assert "Team1" in loaded_data["teams"]


def test_update_team(state_file, game):
    """Test the `update_team` method to ensure the team state is updated and saved."""
    state = State(file_path=state_file, game=game)
    new_team_state = TeamState(name="Team1", goal_location_name=game.locations[0].name)

    state.update_team("Team1", new_team_state)

    # Check the internal state
    assert state.teams["Team1"] == new_team_state

    # Check that the updated state is saved
    with open(state_file, "r") as file:
        saved_data = yaml.safe_load(file)
        assert "Team1" in saved_data["teams"]
        assert saved_data["teams"]["Team1"]["name"] == "Team1"
