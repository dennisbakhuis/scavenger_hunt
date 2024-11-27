"""Tests for the State model."""

import tempfile
import os
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest

from models import State, TeamState, Location, AnswerOption, QuestionType, NextLocationMechanic


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
    assert state.n_active_teams == 0


def test_team_exists(state_file, game):
    """Test that the `team_exists` method correctly checks for team existence."""
    state = State(file_path=state_file, game=game)
    assert not state.team_exists("Team1")

    team_state_file_path = state._team_state_path / "TeamA.yaml"
    team_state_file_path.touch()
    assert state.team_exists("TeamA")


def test_get_or_create_team_state(state_file, game):
    """Test the `get_team_state` method to ensure it returns the correct `TeamState`."""
    state = State(file_path=state_file, game=game)

    # check when team already exists
    team_state_file_path = state._team_state_path / "TeamA.yaml"
    team_state = TeamState(
        name="TeamA", goal_location_name=game.locations[0].name, file_path=team_state_file_path
    )

    loaded_team_state = state.get_or_create_team_state("TeamA")
    assert loaded_team_state.name == team_state.name

    # check when team does not exist
    assert not state.team_exists("TeamB")
    new_team_state = state.get_or_create_team_state("TeamB")
    assert new_team_state.name == "TeamB"
    assert state.team_exists("TeamB")


def test_state_from_yaml(state_file, game):
    """Test the `from_yaml_file` method to ensure a state is loaded correctly from a YAML file."""
    # Test creating a new state when the file does not exist
    if Path(state_file).exists():
        os.remove(state_file)  # Ensure the file does not exist before the test

    state = State.from_yaml_file(state_file, game)
    assert not state.button_beam_to_location_visible
    assert state.next_location_mechanic == NextLocationMechanic.NEAREST_WHEN_CORRECT

    state.button_beam_to_location_visible = True
    state.next_location_mechanic = NextLocationMechanic.RANDOM
    state.save()

    assert Path(state_file).exists()

    new_state = State.from_yaml_file(state_file, game)
    assert new_state.button_beam_to_location_visible
