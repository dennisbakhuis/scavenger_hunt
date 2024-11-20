"""Test project constants."""

import importlib


def test_constants():
    """Test that the constants are set."""
    from constants import (
        GAME_FILE,
        STATE_FILE,
        LOGGING_FILE,
        DEFAULT_GAME_FILE,
        DEFAULT_STATE_FILE,
        DEFAULT_LOGGING_FILE,
    )

    assert isinstance(GAME_FILE, str)
    assert isinstance(STATE_FILE, str)
    assert isinstance(LOGGING_FILE, str)

    assert GAME_FILE == DEFAULT_GAME_FILE
    assert STATE_FILE == DEFAULT_STATE_FILE
    assert LOGGING_FILE == DEFAULT_LOGGING_FILE


def test_overwritten_constants(monkeypatch):
    """Test that the constants are overwritten."""
    monkeypatch.setenv("GAME_FILE", "test_game.yaml")
    monkeypatch.setenv("STATE_FILE", "test_state.yaml")
    monkeypatch.setenv("LOGGING_FILE", "test_log.ndjson")

    import constants as constants

    importlib.reload(constants)

    assert constants.GAME_FILE == "test_game.yaml"
    assert constants.STATE_FILE == "test_state.yaml"
    assert constants.LOGGING_FILE == "test_log.ndjson"
