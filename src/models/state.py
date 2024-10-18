"""Game state model."""
from pathlib import Path
from random import choice

from pydantic import BaseModel, PrivateAttr
import yaml

from .team_state import TeamState
from .game import Game


class State(BaseModel):
    """
    Represents the overall game state, containing information about all team states.

    Parameters
    ----------
    team_states : dict[str, TeamState], optional
        A dictionary where keys are team names and values are their respective `TeamState` objects. Defaults to an empty dictionary.

    Properties
    ----------
    n_active_teams : int
        The number of currently active teams in the game.
    """

    teams: dict[str, TeamState] = {}

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
        self._game = game

    @property
    def n_active_teams(self):
        """
        Returns the number of active teams.

        Returns
        -------
        int
            The number of teams currently active in the game.
        """
        return len(self.teams)

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
        return team_name in self.teams

    def get_team_state(self, team_name: str) -> TeamState:
        """
        Get the state of a team by name.

        Raises
        ------
        ValueError
            If the team does not exist in the state.

        Parameters
        ----------
        team_name : str
            The name of the team.

        Returns
        -------
        TeamState
            The state of the team.
        """
        if self.team_exists(team_name):
            return self.teams[team_name]

        raise ValueError(f"Team '{team_name}' does not exist in the game state.")

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
            with open(file_path, "r") as file:
                state_data = yaml.safe_load(file)
                state = cls(file_path=file_path, game=game, **state_data)

        return state

    def save(self) -> None:
        """
        Save the game state to a YAML file.

        Parameters
        ----------
        file_path : str
            The path to the YAML file.
        """
        with open(self._file_path, "w") as file:
            yaml.dump(
                data=self.model_dump(),
                stream=file,
                default_flow_style=False,
            )

    def get_or_create_team(self, team_name: str) -> TeamState:
        """
        Get the state of a team by name, creating a new team if it does not exist.

        Parameters
        ----------
        team_name : str
            The name of the team.

        Returns
        -------
        TeamState
            The state of the team.
        """
        if not self.team_exists(team_name):
            self.teams[team_name] = TeamState(
                name=team_name,
                goal=choice(self._game.locations),
            )

            self.save()

        return self.teams[team_name]

    def update_team(self, team_name: str, new_state: TeamState) -> None:
        """
        Update the state of a team.

        Parameters
        ----------
        team_name : str
            The name of the team.
        new_state : TeamState
            The new state of the team.
        """
        self.teams[team_name] = new_state
        self.save()
