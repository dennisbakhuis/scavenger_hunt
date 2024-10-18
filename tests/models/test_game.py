"""Tests for the Game model."""
import yaml

from models import Game


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
