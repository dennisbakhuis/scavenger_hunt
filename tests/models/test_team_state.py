"""Tests for the State model."""

import tempfile
from pathlib import Path

from models.team_state import TeamState


def test_team_state_creation():
    """
    Test the creation of the `TeamState` class.

    Tests
    -----
    - Ensures that the `name`, `goal`, and `solved` attributes are correctly assigned.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = f"{temp_dir}/team_state.yaml"

        team = TeamState(
            name="Team A",
            goal_location_name="Location A",
            solved={"Location1": 10},
            file_path=file_path,
        )
        assert team.name == "Team A"
        assert team.goal_location_name == "Location A"
        assert team.solved["Location1"] == 10

        assert Path(file_path).exists()
