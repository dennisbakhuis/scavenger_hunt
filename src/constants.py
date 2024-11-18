"""
Constants for the project.

Default values are provided for the following environment variables:
- `GAME_FILE`: The path to the game data file.
- `STATE_FILE`: The path to the application state file.
- `LOGGING_FILE`: The path to the location logging file.

If the environment variables are not set, the default values are used.
"""
import os

DEFAULT_GAME_FILE = "game_data/game.yaml"
DEFAULT_STATE_FILE = "state/application_state.yaml"
DEFAULT_LOGGING_FILE = "state/location_log.ndjson"

GAME_FILE = os.environ.get("GAME_FILE", DEFAULT_GAME_FILE)
STATE_FILE = os.environ.get("STATE_FILE", DEFAULT_STATE_FILE)
LOGGING_FILE = os.environ.get("LOGGING_FILE", DEFAULT_LOGGING_FILE)
