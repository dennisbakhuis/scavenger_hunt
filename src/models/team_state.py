"""Model for the state of a team in the game."""

from pathlib import Path

from pydantic import BaseModel, PrivateAttr
import yaml


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
    goal_location_name: str
    solved: dict[str, int] = {}

    _file_path: str = PrivateAttr(init=True)

    def __init__(
        self,
        file_path: str,
        **data,
    ):
        """
        Initialize the game state.

        Parameters
        ----------
        file_path : str
            The path to the YAML file storing the game state.
        """
        super().__init__(**data)
        self._file_path = file_path

        if not Path(self._file_path).exists():
            self.save()

    def save(self) -> None:
        """Save the team state to a YAML file."""
        with open(self._file_path, "w") as file:
            yaml.dump(
                data=self.model_dump(),
                stream=file,
                default_flow_style=False,
            )
