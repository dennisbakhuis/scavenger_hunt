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

    def __init__(self, file_path: str, **data):
        """Initialize the game object."""
        super().__init__(**data)
        self._file_path = file_path

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
            game = cls(file_path=file_path, **game_data)

        return game

    def get_location_by_name(self, location_name: str) -> Location:
        """
        Get a location by name.

        Parameters
        ----------
        location_name : str
            The name of the location to get.

        Returns
        -------
        Location
            The location object.
        """
        for location in self.locations:
            if location.name == location_name:
                return location

        raise ValueError(f"Location '{location_name}' not found in the game.")

    @property
    def file_path(self) -> str:
        """Return the file path of the game data."""
        return self._file_path
