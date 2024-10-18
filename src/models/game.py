"""Game model for the API."""
import yaml

from pydantic import BaseModel, PrivateAttr

from .location import Location


class Game(BaseModel):
    """
    Represents a game that contains multiple locations and a radius.

    Parameters
    ----------
    locations : list[Location]
        A list of locations included in the game.
    radius : int
        The radius around each location for the game logic.
    """

    locations: list[Location]
    radius: int

    _file_path: str = PrivateAttr(init=True)

    @classmethod
    def from_yaml_file(cls, file_path: str) -> "Game":
        """
        Load game data from a YAML file.

        Parameters
        ----------
        file_path : str
            The path to the YAML file containing the game data.

        Returns
        -------
        State
            The game state object.
        """
        with open(file_path, "r") as file:
            game_data = yaml.safe_load(file)
            game = cls(**game_data)
            game._file_path = file_path

        return game

