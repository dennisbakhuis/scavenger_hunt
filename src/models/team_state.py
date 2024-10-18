"""Model for the state of a team in the game."""
from pydantic import BaseModel

from .location import Location


class TeamState(BaseModel):
    """
    Represents the state of a team in the game.

    Parameters
    ----------
    name : str
        The name of the team.
    goal : Location
        The current goal (location) of the team.
    solved : dict[str, int], optional
        A dictionary where keys are location names and values are scores for solved locations. Defaults to an empty dictionary.
    """

    name: str
    goal: Location
    solved: dict[str, int] = {}
