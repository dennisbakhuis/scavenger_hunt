"""Handle the display and answering of the question."""

from pathlib import Path
import streamlit as st
from models import QuestionType, Location, TeamState, Game, AnswerOption
from .determine_next_location import determine_next_location


def display_question(
    goal_location: Location,
    base_question_path: Path,
):
    """
    Display the question header, subheader, and image if available.

    Parameters
    ----------
    goal_location : Location
        The location object containing question details.
    base_question_path : Path
        The base path for accessing the image file.
    """
    st.header(f"Question ({goal_location.question_type.value})")
    st.subheader(goal_location.name)
    st.markdown(goal_location.question)

    image_file = base_question_path / goal_location.image
    if image_file.exists():
        st.image(str(image_file), use_container_width=True)


def handle_answer_submission(
    answer: str,
    options: list[AnswerOption],
    team_state: TeamState,
    goal_location: Location,
    game: Game,
):
    """
    Handle answer submission for open questions.

    Parameters
    ----------
    answer : str
        The user's input answer.
    options : list
        A list of possible answers (with their scores).
    team_state : TeamState
        The state of the team submitting the answer.
    goal_location : Location
        The current goal location being processed.
    """
    lowered_answer = answer.lower()

    score = next(
        (option.score for option in options if option.option.lower() == lowered_answer),
        next(
            (option.score for option in options if option.option in ["", "wrong"]), options[0].score
        ),  # Default to the first option's score
    )
    team_state.solved[goal_location.name] = score

    update_team_state(team_state, score, goal_location, game)


def handle_button_click(
    option: AnswerOption,
    team_state: TeamState,
    goal_location: Location,
    game: Game,
):
    """
    Handle button click for multiple-choice or 'don't know' answers.

    Parameters
    ----------
    option : object
        The selected option (contains the option text and score).
    team_state : TeamState
        The state of the team selecting the option.
    goal_location : Location
        The current goal location being processed.
    game : Game
        The game instance containing game-wide data.
    state : State
        The state object used to update team progress.
    """
    team_state.solved[goal_location.name] = option.score
    update_team_state(team_state, option.score, goal_location, game)


def update_team_state(
    team_state: TeamState,
    score: int,
    goal_location: Location,
    game: Game,
):
    """
    Update the team state and determine the next goal location.

    Parameters
    ----------
    team_state : TeamState
        The current state of the team being updated.
    score : int
        The score assigned for the current answer.
    goal_location : Location
        The location where the question is being answered.
    game : Game
        The game instance that holds location data.
    state : State
        The state object used to persist updates.
    """
    if len(game.locations) - len(team_state.solved) > 0:
        next_goal_location_name = determine_next_location(
            team_state=team_state,
            game=game,
            previous_score=score,
            current_location=goal_location.coordinates,
        )
        team_state.goal_location_name = next_goal_location_name

    team_state.save()


def handle_question(goal_location: Location, team_state: TeamState, game: Game):
    """
    Handle the display and interaction of the question.

    Parameters
    ----------
    goal_location : Location
        The location object containing the question details.
    team_state : TeamState
        The current state of the team interacting with the question.
    game : Game
        The game instance containing all locations.
    state : State
        The state object used to persist updates.
    """
    base_question_path = Path(game.file_path).parent
    display_question(goal_location, base_question_path)

    st.subheader("Answer:")

    if goal_location.question_type == QuestionType.MultipleChoice:
        for option in goal_location.answer:
            st.button(
                label=option.option,
                on_click=lambda option=option: handle_button_click(
                    option=option,
                    team_state=team_state,
                    goal_location=goal_location,
                    game=game,
                ),
            )
    elif goal_location.question_type == QuestionType.OpenQuestion:
        answer = st.text_input("Answer:")
        st.button(
            label="Submit",
            on_click=lambda: handle_answer_submission(
                answer=answer,
                options=goal_location.answer,
                team_state=team_state,
                goal_location=goal_location,
                game=game,
            ),
        )

    if goal_location.dont_know_answer:
        st.button(
            label=goal_location.dont_know_answer.option,
            on_click=lambda: handle_button_click(
                option=goal_location.dont_know_answer,
                team_state=team_state,
                goal_location=goal_location,
                game=game,
            ),
        )
