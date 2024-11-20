"""Method to determine the next location for a team based on their current state, game information, and previous score."""

from random import choice
from geopy.distance import geodesic

from models import Game, TeamState


def determine_next_location(
    team_state: TeamState,
    game: Game,
    previous_score: int,
    current_location: tuple[float, float],
) -> str:
    """
    Determine the next location for a team based on their current state, game information, and previous score.

    Parameters
    ----------
    team_state : TeamState
        The current state of the team, including solved locations.
    game : Game
        The current game information, including available locations.
    previous_score : int
        The score from the previous round. A positive score indicates success, and a negative score indicates failure.
    current_location : tuple of float
        The current latitude and longitude of the team in decimal degrees.

    Returns
    -------
    Location
        The next location for the team, selected from the unsolved locations, based on the previous score and distance.
        If the previous score is positive, the closest location is returned. If the score is negative, the farthest location
        is returned. If the score is neutral (zero), a random unsolved location is chosen.
    """
    unsolved_locations = [
        location for location in game.locations if location.name not in team_state.solved
    ]

    sorted_by_distance = sorted(
        unsolved_locations,
        key=lambda location: geodesic(
            (location.latitude, location.longitude), current_location
        ).meters,
    )

    if previous_score > 0:
        next_location = sorted_by_distance[0]
    elif previous_score < 0:
        next_location = sorted_by_distance[-1]
    else:
        next_location = choice(sorted_by_distance)  # nosec

    return next_location.name
