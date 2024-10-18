"""Tests for the State model."""
from models.location import Location
from models.answer_option import AnswerOption


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
        options=options,
        description="A beautiful park",
        image="image.png"
    )
    assert location.name == "Park"
    assert location.latitude == 40.7128
    assert location.longitude == -74.0060
    assert len(location.options) == 2
    assert location.options[0].option == "Option A"
    assert location.description == "A beautiful park"
    assert location.image == "image.png"
