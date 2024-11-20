"""Tests for provided game data."""

from pathlib import Path

from models import Game
from constants import GAME_FILE


game = Game.from_yaml_file(file_path=GAME_FILE)


def test_images_exist():
    """Test that all images exist."""
    base_question_path = Path(game.file_path).parent

    for location in game.locations:
        image_file = base_question_path / location.image
        assert image_file.exists()
