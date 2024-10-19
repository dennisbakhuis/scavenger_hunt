"""Tests for the determine_next_location function."""
from random import seed

import pytest
from unittest.mock import MagicMock

from models import Location, TeamState, Game, AnswerOption, QuestionType
from helpers.determine_next_location import determine_next_location


def create_location(
    name: str,
    latitude: float,
    longitude: float,
) -> Location:
    """Create a `Location` object for testing."""
    return Location(
        name=name,
        latitude=latitude,
        longitude=longitude,
        question_type=QuestionType.MultipleChoice,
        question="A test location.",
        image="test_image.png",
        answer=[AnswerOption(option="Option A", score=10)],
    )


@pytest.fixture
def mock_game() -> MagicMock:
    """Create a `MagicMock` for the `Game` object for testing."""
    game = MagicMock(Game)
    game.locations = [
        create_location("Location A", 0.0, 0.0),
        create_location("Location B", 1.0, 1.0),
        create_location("Location C", 2.0, 2.0),
        create_location("Location D", 0.5, 0.5),
    ]
    return game


@pytest.fixture
def mock_team_state() -> TeamState:
    """Create a mock TeamState object for testing."""
    return TeamState(
        name="Team X",
        goal_location_name="Location A",
        solved={},
    )


def test_next_location_positive_score(mock_team_state, mock_game):
    """Test that the closest location is chosen when the previous score is positive."""
    current_location = (0.0, 0.0)
    previous_score = 1

    # Expect the closest location to be "Location A" it is exactly at (0.0, 0.0)
    next_location = determine_next_location(mock_team_state, mock_game, previous_score, current_location)
    assert next_location == "Location A"

    # Set the "Location A" as solved; expect the next closest location to be "Location D"
    mock_team_state.solved["Location A"] = 1
    next_location = determine_next_location(mock_team_state, mock_game, previous_score, current_location)
    assert next_location == "Location D"


def test_next_location_negative_score(mock_team_state, mock_game):
    """Test that the farthest location is chosen when the previous score is negative."""
    current_location = (0.0, 0.0)
    previous_score = -1

    # Expect the farthest location to be "Location C"
    next_location = determine_next_location(mock_team_state, mock_game, previous_score, current_location)
    assert next_location == "Location C"

    # Set "Location C" as solved; expect the next farthest location to be "Location B"
    mock_team_state.solved["Location C"] = 1
    next_location = determine_next_location(mock_team_state, mock_game, previous_score, current_location)
    assert next_location == "Location B"


def test_next_location_zero_score(mock_team_state, mock_game):
    """Test that a random location is chosen when the previous score is zero."""
    current_location = (0.0, 0.0)
    previous_score = 0

    # Set a fixed random seed to make the test deterministic
    seed(1)
    next_location = determine_next_location(mock_team_state, mock_game, previous_score, current_location)
    assert next_location == "Location D"

    # Set "Location C" as solved and test again
    mock_team_state.solved["Location C"] = 1
    seed(1)
    next_location = determine_next_location(mock_team_state, mock_game, previous_score, current_location)
    assert next_location == "Location A"


def test_no_unsolved_locations(mock_team_state, mock_game):
    """Test that no location is chosen when all locations are solved."""
    current_location = (0.0, 0.0)
    previous_score = 1

    # Mark all locations as solved
    mock_team_state.solved = {
        "Location A": 1,
        "Location B": 1,
        "Location C": 1,
        "Location D": 1,
    }

    with pytest.raises(IndexError):
        determine_next_location(mock_team_state, mock_game, previous_score, current_location)


def test_next_location_unsolved(mock_team_state, mock_game):
    """Test that the next location is chosen correctly when no locations are solved."""
    current_location = (0.0, 0.0)
    previous_score = 1

    # Expect "Location A" to be chosen first, since no locations are solved
    next_location = determine_next_location(mock_team_state, mock_game, previous_score, current_location)
    assert next_location == "Location A"

    # Set "Location A" as solved and expect "Location D" to be chosen next
    mock_team_state.solved["Location A"] = 1
    next_location = determine_next_location(mock_team_state, mock_game, previous_score, current_location)
    assert next_location == "Location D"


def test_all_locations_unsolved(mock_team_state, mock_game):
    """Test that the function works when no locations are solved."""
    current_location = (0.0, 0.0)
    previous_score = 10

    # Since no locations are solved, the closest location should be "Location A"
    next_location = determine_next_location(mock_team_state, mock_game, previous_score, current_location)
    assert next_location == "Location A"
