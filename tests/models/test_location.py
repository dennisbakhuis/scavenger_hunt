"""Tests for the State model."""
from models import Location, AnswerOption, QuestionType


def test_location_creation():
    """
    Test the creation of the `Location` class.

    Tests
    -----
    - Ensures the `name`, `latitude`, `longitude`, `options`, `description`,
      and `image` attributes are correctly assigned.
    """
    options = [AnswerOption(option="Option A", score=10), AnswerOption(option="Option B", score=5)]
    location = Location(
        name="Park",
        latitude=40.7128,
        longitude=-74.0060,
        question_type=QuestionType.MultipleChoice,
        question="A beautiful park",
        answer=options,
        image="image.png"
    )
    assert location.name == "Park"
    assert location.latitude == 40.7128
    assert location.longitude == -74.0060
    assert len(location.answer) == 2
    assert location.answer[0].option == "Option A"
    assert location.question == "A beautiful park"
    assert location.image == "image.png"
    assert location.question_type == QuestionType.MultipleChoice
    assert location.coordinates == (40.7128, -74.0060)
