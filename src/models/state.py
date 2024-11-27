"""Game state model."""

from enum import Enum
from pathlib import Path
from random import choice

from pydantic import BaseModel, PrivateAttr, field_serializer
import yaml

from .team_state import TeamState
from .game import Game


class NextLocationMechanic(str, Enum):
    """Mechanics for selecting the next location for a team."""

    RANDOM = "random"
    NEAREST = "nearest"
    FURTHEST = "furthest"
    NEAREST_WHEN_CORRECT = "nearest_when_correct"
    FURTHEST_WHEN_CORRECT = "furthest_when_correct"


class State(BaseModel):
    """
    Represents the overall game state, containing information about all team states.

    Parameters
    ----------
    button_beam_to_location_visible : bool, optional (default=False)
        Adds a button to beam to goal location. Defaults to False.

    Properties
    ----------
    n_active_teams : int
        The number of currently active teams in the game.
    """

    button_beam_to_location_visible: bool = False
    next_location_mechanic: NextLocationMechanic = NextLocationMechanic.NEAREST_WHEN_CORRECT

    _file_path: str = PrivateAttr(init=True)
    _game: Game = PrivateAttr(init=True)

    def __init__(
        self,
        file_path: str,
        game: Game,
        **data,
    ):
        """
        Initialize the game state.

        Parameters
        ----------
        file_path : str
            The path to the YAML file storing the game state.
        game : Game
            The game object holding the game data.
        """
        super().__init__(**data)
        self._file_path = file_path
        self._team_state_path = Path(file_path).parent / "team_states"
        self._game = game

        if not self._team_state_path.exists():
            self._team_state_path.mkdir()

        if not Path(self._file_path).exists():
            self.save()

    @field_serializer("next_location_mechanic")
    def serialize_enum(self, next_location_mechanic: NextLocationMechanic, _) -> str:
        """Serialize the mapping to a dict and use the Enum keys instead of values."""
        return next_location_mechanic.value

    @property
    def n_active_teams(self):
        """
        Returns the number of registered teams.

        Returns
        -------
        int
            The number of teams currently active in the game.
        """
        team_states = self._team_state_path.glob("*.yaml")
        return len(list(team_states))

    def team_exists(self, team_name: str) -> bool:
        """
        Check if a team exists in the state.

        Parameters
        ----------
        team_name : str
            The name of the team.

        Returns
        -------
        bool
            True if the team exists, False otherwise.
        """
        team_state_file = self._team_state_path / f"{team_name}.yaml"
        return team_state_file.exists()

    def get_or_create_team_state(self, team_name: str) -> TeamState:
        """
        Get the state of a team by name, creating it if it does not exist.

        Parameters
        ----------
        team_name : str
            The name of the team.

        Returns
        -------
        TeamState
            The state of the team.
        """
        team_state_file = self._team_state_path / f"{team_name}.yaml"

        if team_state_file.exists():
            with open(team_state_file, "r") as file:
                team_data = yaml.safe_load(file)
                return TeamState(
                    file_path=str(team_state_file),
                    **team_data,
                )

        goal_location = choice(self._game.locations)  # nosec
        return TeamState(
            file_path=str(self._team_state_path / f"{team_name}.yaml"),
            name=team_name,
            goal_location_name=goal_location.name,
        )

    @classmethod
    def from_yaml_file(cls, file_path: str, game: Game) -> "State":
        """
        Create or load a `State` object from a YAML file.

        Parameters
        ----------
        file_path : str
            The path to the YAML file containing the state data.
        game : Game
            The game object holding the game data.

        Returns
        -------
        State
            The state object.
        """
        if not Path(file_path).exists():
            state = cls(file_path=file_path, game=game)
        else:
            with open(file_path, "r") as f:
                state_data = yaml.safe_load(f)
                state = cls(file_path=file_path, game=game, **state_data)

        return state

    def save(self) -> None:
        """Save the game state to a YAML file."""
        with open(self._file_path, "w") as f:
            yaml.dump(
                data=self.model_dump(),
                stream=f,
            )

    def get_teams_as_dict(self) -> dict:
        """
        Get all team states as a dictionary.

        Returns
        -------
        dict
            A dictionary where keys are team names and values are team states.
        """
        teams = {}
        for team_state_file in self._team_state_path.glob("*.yaml"):
            with open(team_state_file, "r") as file:
                team_data = yaml.safe_load(file)
                team_name = team_state_file.stem
                teams[team_name] = TeamState(
                    file_path=str(team_state_file),
                    **team_data,
                )

        return teams
