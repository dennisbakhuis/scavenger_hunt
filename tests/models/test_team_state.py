"""Tests for the State model."""
from models.team_state import TeamState


def test_team_state_creation():
    """
    Test the creation of the `TeamState` class.

    Tests
    -----
    - Ensures that the `name`, `goal`, and `solved` attributes are correctly assigned.
    """
    team = TeamState(name="Team A", goal_location_name="Location A", solved={"Location1": 10})
    assert team.name == "Team A"
    assert team.goal_location_name == "Location A"
    assert team.solved["Location1"] == 10
