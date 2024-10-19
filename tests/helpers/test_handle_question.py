"""Tests for the handle_question function."""
from unittest.mock import MagicMock, patch
from pathlib import Path

import pytest
import streamlit as st

from models import Location, TeamState, Game, State, QuestionType, AnswerOption
from helpers.handle_question import handle_answer_submission, handle_button_click, handle_question, display_question, update_team_state


@pytest.fixture(autouse=True)
def mock_streamlit():
    with patch("streamlit.header"), \
         patch("streamlit.subheader"), \
         patch("streamlit.markdown"), \
         patch("streamlit.image"), \
         patch("streamlit.text_input", return_value="mocked_input"), \
         patch("streamlit.button", return_value=False), \
         patch("streamlit.rerun", side_effect=RuntimeError("Mocked rerun")):
        yield

@pytest.fixture
def mock_game():
    return Game(
        file_path="game.yaml",
        locations=[Location(name="Park", latitude=0, longitude=0, options=[], description="", image="", question_type=QuestionType.MultipleChoice, question="", answer=[AnswerOption(option="A", score=10)])],
        radius=100,
    )


@pytest.fixture
def mock_state():
    state = MagicMock(spec=State)
    state.update_team = MagicMock()
    return state


@pytest.fixture
def mock_team_state():
    return TeamState(
        name="Team A",
        goal_location_name="Park",
        solved={},
)


@pytest.fixture
def mock_goal_location():
    return Location(name="Park", latitude=0, longitude=0, options=[], description="", image="image.png", question_type=QuestionType.MultipleChoice, question="What is the capital?", answer=[AnswerOption(option="A", score=10)])


def test_display_question(mock_goal_location):
    base_question_path = Path("/some/path")
    with patch("pathlib.Path.exists", return_value=True):
        display_question(mock_goal_location, base_question_path)
        st.header.assert_called_once_with("Question (multiple choice)")
        st.subheader.assert_called_once_with(mock_goal_location.name)
        st.markdown.assert_called_once_with(mock_goal_location.question)
        st.image.assert_called_once()


# def test_handle_answer_submission(mock_team_state, mock_goal_location, mock_game, mock_state):
#     answer = "A"
#     options = [AnswerOption(option="A", score=10)]
#     with patch("helpers.handle_question.update_team_state") as mock_update_team_state:
#         handle_answer_submission(answer, options, mock_team_state, mock_goal_location, mock_game, mock_state)
        # mock_update_team_state.assert_called_once_with(mock_team_state, 10, mock_goal_location, mock_game, mock_state)


def test_handle_button_click(mock_team_state, mock_goal_location, mock_game, mock_state):
    option = AnswerOption(option="A", score=10)
    with patch("helpers.handle_question.update_team_state") as mock_update_team_state:
        handle_button_click(option, mock_team_state, mock_goal_location, mock_game, mock_state)
        mock_update_team_state.assert_called_once_with(mock_team_state, 10, mock_goal_location, mock_game, mock_state)

