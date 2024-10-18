"""Tests for the `AnswerOption` class."""
from models.answer_option import AnswerOption

def test_answer_option_creation():
    """
    Test the creation of the `AnswerOption` class.

    Tests
    -----
    - Checks if the `option` and `score` attributes are correctly assigned.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    answer_option = AnswerOption(option="Option A", score=10)
    assert answer_option.option == "Option A"
    assert answer_option.score == 10
