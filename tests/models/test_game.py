"""Tests for the Game model."""
import tempfile
import yaml
import pytest
from models import Game, Location, AnswerOption, QuestionType


GAME_DATA_FILE = "data/game.yaml"


def test_game_model_data():
    """Test the Game model with the actual game data."""
    with open(GAME_DATA_FILE, "r") as file:
        game_data = yaml.safe_load(file)
        game = Game.model_validate(game_data)

    assert isinstance(game, Game)

    other_game = Game.from_yaml_file(file_path=GAME_DATA_FILE)

    assert game != other_game
    game._file_path = GAME_DATA_FILE
    assert game == other_game

    assert other_game._file_path == GAME_DATA_FILE
    assert other_game.file_path == GAME_DATA_FILE


def create_location(
    name: str,
    latitude: float,
    longitude: float,
    *args,
    **kwargs,
) -> Location:
    """Create a `Location` object."""
    return Location(
        name=name,
        latitude=latitude,
        longitude=longitude,
        question_type=QuestionType.MultipleChoice,
        question="A test location.",
        answer=[AnswerOption(option="Option A", score=10)],
        image="test_image.png",
    )


@pytest.fixture
def sample_game_data() -> dict:
    """Fixture to provide sample game data."""
    return {
        "locations": [
            {
                "name": "Location A",
                "latitude": 0.0,
                "longitude": 0.0,
                "question_type": "multiple choice",
                "question": "Test Location A",
                "image": "image_a.png",
                "answer": [{"option": "Option A", "score": 10}],
            },
            {
                "name": "Location B",
                "latitude": 1.0,
                "longitude": 1.0,
                "question_type": "multiple choice",
                "question": "Test Location B",
                "image": "image_b.png",
                "answer": [{"option": "Option B", "score": 20}],
            }
        ],
        "radius": 100
    }


def test_game_creation(sample_game_data):
    """Test the creation of a Game object."""
    locations = [create_location(**loc) for loc in sample_game_data["locations"]]
    game = Game(locations=locations, radius=sample_game_data["radius"])

    assert len(game.locations) == 2
    assert game.radius == 100
    assert game.locations[0].name == "Location A"
    assert game.locations[1].name == "Location B"


def test_game_from_yaml_file(sample_game_data):
    """Test loading game data from a YAML file."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="t+w") as temp_file:
        yaml.dump(sample_game_data, temp_file)
        file_path = temp_file.name
        game = Game.from_yaml_file(file_path)

    assert len(game.locations) == 2
    assert game.radius == 100
    assert game.locations[0].name == "Location A"
    assert game.locations[1].name == "Location B"


def test_game_get_location_by_name(sample_game_data):
    """Test retrieving a location by name."""
    locations = [create_location(**loc) for loc in sample_game_data["locations"]]
    game = Game(locations=locations, radius=sample_game_data["radius"])

    location_a = game.get_location_by_name("Location A")
    assert location_a.name == "Location A"
    assert location_a.latitude == 0.0

    location_b = game.get_location_by_name("Location B")
    assert location_b.name == "Location B"
    assert location_b.latitude == 1.0


def test_game_get_location_by_name_not_found(sample_game_data):
    """Test retrieving a location that doesn't exist raises a ValueError."""
    locations = [create_location(**loc) for loc in sample_game_data["locations"]]
    game = Game(locations=locations, radius=sample_game_data["radius"])

    with pytest.raises(ValueError, match="Location 'Location C' not found in the game."):
        game.get_location_by_name("Location C")


def test_game_yaml_file_not_found():
    """Test that attempting to load from a non-existent file raises a FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        Game.from_yaml_file("non_existent_file.yaml")
