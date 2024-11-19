"""Tests for the handle_question function."""
from unittest.mock import MagicMock, patch
from pathlib import Path

import pytest
import streamlit as st

from models import Location, TeamState, Game, State, QuestionType, AnswerOption
from helpers.handle_question import handle_answer_submission, handle_button_click, handle_question, display_question, update_team_state


@pytest.fixture(autouse=True)
def mock_streamlit():
    """
    Fixture to mock Streamlit components.

    Yields
    ------
    None
        Mocked Streamlit components are automatically used during test execution.
    """
    with patch("streamlit.header"), \
         patch("streamlit.subheader"), \
         patch("streamlit.markdown"), \
         patch("streamlit.image"), \
         patch("streamlit.text_input", return_value="mocked_input"), \
         patch("streamlit.button", return_value=False), \
         patch("streamlit.rerun"):
        yield


@pytest.fixture
def mock_game():
    """
    Fixture to provide a mock `Game` instance.

    Returns
    -------
    Game
        A mocked game object with predefined locations and radius.
    """
    return Game(
        file_path="game.yaml",
        locations=[
            Location(name="Park", latitude=0, longitude=0, options=[], description="", image="", question_type=QuestionType.MultipleChoice, question="", answer=[AnswerOption(option="A", score=10)]),
            Location(name="Hotel", latitude=1, longitude=1, options=[], description="", image="", question_type=QuestionType.MultipleChoice, question="", answer=[AnswerOption(option="A", score=10)]),
        ],
        radius=100,
    )


@pytest.fixture
def mock_state():
    """
    Fixture to provide a mock `State` instance.

    Returns
    -------
    MagicMock
        A mocked `State` object with `update_team` method.
    """
    state = MagicMock(spec=State)
    state.update_team = MagicMock()
    return state


@pytest.fixture
def mock_team_state():
    """
    Fixture to provide a mock `TeamState` instance.

    Returns
    -------
    TeamState
        A mocked `TeamState` object.
    """
    return TeamState(
        name="Team A",
        goal_location_name="Park",
        solved={},
    )


@pytest.fixture
def mock_goal_location():
    """
    Fixture to provide a mock goal `Location` instance.

    Returns
    -------
    Location
        A mocked `Location` object representing the goal.
    """
    return Location(name="Park", latitude=0, longitude=0, options=[], description="", image="image.png", question_type=QuestionType.MultipleChoice, question="What is the capital?", answer=[AnswerOption(option="A", score=10)])


def test_display_question(mock_goal_location):
    """
    Test the `display_question` function.

    Parameters
    ----------
    mock_goal_location : Location
        The mock goal location used in the test.
    """
    base_question_path = Path("/some/path")
    with patch("pathlib.Path.exists", return_value=True):
        display_question(mock_goal_location, base_question_path)
        st.header.assert_called_once_with("Question (multiple choice)")
        st.subheader.assert_called_once_with(mock_goal_location.name)
        st.markdown.assert_called_once_with(mock_goal_location.question)
        st.image.assert_called_once()


def test_handle_answer_submission(mock_team_state, mock_goal_location, mock_game, mock_state):
    """
    Test the `handle_answer_submission` function.

    Parameters
    ----------
    mock_team_state : TeamState
        Mocked team state object.
    mock_goal_location : Location
        Mocked goal location.
    mock_game : Game
        Mocked game object.
    mock_state : State
        Mocked state object.
    """
    options = [
        AnswerOption(option="A", score=10),
        AnswerOption(option="B", score=5),
        AnswerOption(option="", score=-10),
    ]

    with patch("helpers.handle_question.update_team_state") as mock_update_team_state:
        handle_answer_submission("A", options, mock_team_state, mock_goal_location, mock_game, mock_state)
        mock_update_team_state.assert_called_once_with(mock_team_state, 10, mock_goal_location, mock_game, mock_state)

    with patch("helpers.handle_question.update_team_state") as mock_update_team_state:
        handle_answer_submission("b", options, mock_team_state, mock_goal_location, mock_game, mock_state)
        mock_update_team_state.assert_called_once_with(mock_team_state, 5, mock_goal_location, mock_game, mock_state)

    with patch("helpers.handle_question.update_team_state") as mock_update_team_state:
        handle_answer_submission("hello", options, mock_team_state, mock_goal_location, mock_game, mock_state)
        mock_update_team_state.assert_called_once_with(mock_team_state, -10, mock_goal_location, mock_game, mock_state)


def test_handle_button_click(mock_team_state, mock_goal_location, mock_game, mock_state):
    """
    Test the `handle_button_click` function.

    Parameters
    ----------
    mock_team_state : TeamState
        Mocked team state object.
    mock_goal_location : Location
        Mocked goal location.
    mock_game : Game
        Mocked game object.
    mock_state : State
        Mocked state object.
    """
    option = AnswerOption(option="A", score=10)
    with patch("helpers.handle_question.update_team_state") as mock_update_team_state:
        handle_button_click(option, mock_team_state, mock_goal_location, mock_game, mock_state)
        mock_update_team_state.assert_called_once_with(mock_team_state, 10, mock_goal_location, mock_game, mock_state)


def test_update_team_state_with_locations(mock_team_state, mock_goal_location, mock_game, mock_state):
    """
    Test `update_team_state` function for transitioning between locations.

    Parameters
    ----------
    mock_team_state : TeamState
        Mocked team state object.
    mock_goal_location : Location
        Mocked goal location.
    mock_game : Game
        Mocked game object.
    mock_state : State
        Mocked state object.
    """
    mock_team_state.solved = {"Park": 10}
    update_team_state(mock_team_state, 10, mock_goal_location, mock_game, mock_state)
    mock_state.update_team.assert_called_once_with(mock_team_state.name, mock_team_state)
    assert mock_team_state.goal_location_name == "Hotel"


def test_update_team_state_all_solved(mock_team_state, mock_goal_location, mock_game, mock_state):
    """
    Test `update_team_state` function when all locations are solved.

    Parameters
    ----------
    mock_team_state : TeamState
        Mocked team state object.
    mock_goal_location : Location
        Mocked goal location.
    mock_game : Game
        Mocked game object.
    mock_state : State
        Mocked state object.
    """
    mock_team_state.solved = {"Park": 10, "Hotel": 10}
    update_team_state(mock_team_state, 10, mock_goal_location, mock_game, mock_state)
    mock_state.update_team.assert_not_called()
    assert mock_team_state.goal_location_name == "Park"


def test_handle_question(mock_game, mock_team_state, mock_goal_location, mock_state):
    """
    Test `handle_question` function.

    Parameters
    ----------
    mock_game : Game
        Mocked game object.
    mock_team_state : TeamState
        Mocked team state object.
    mock_goal_location : Location
        Mocked goal location.
    mock_state : State
        Mocked state object.
    """
    with patch("helpers.handle_question.display_question") as mock_display_question:
        handle_question(mock_goal_location, mock_team_state, mock_game, mock_state)
        mock_display_question.assert_called_once_with(mock_goal_location, Path("images").parent)
