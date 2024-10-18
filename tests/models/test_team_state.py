"""Tests for the State model."""
from models.team_state import TeamState
from models.location import Location

def test_team_state_creation():
    """
    Test the creation of the `TeamState` class.

    Tests
    -----
    - Ensures that the `name`, `goal`, and `solved` attributes are correctly assigned.
    """
    goal_location = Location(
        name="Park",
        latitude=40.7128,
        longitude=-74.0060,
        options=[],
        description="A beautiful park",
        image="image.png"
    )
    team = TeamState(name="Team A", goal=goal_location, solved={"Location1": 10})
    assert team.name == "Team A"
    assert team.goal == goal_location
    assert team.solved["Location1"] == 10
