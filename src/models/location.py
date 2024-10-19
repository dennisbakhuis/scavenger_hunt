"""Model for a location in the game."""
from pydantic import BaseModel

from .answer_option import AnswerOption
from .question_type import QuestionType


class Location(BaseModel):
    """
    Represents a geographical location with a question and answer options.

    Parameters
    ----------
    name : str
        The name of the location.
    latitude : float
        The latitude coordinate of the location.
    longitude : float
        The longitude coordinate of the location.
    introduction_markdown_file : str
        A markdown file containing an introduction for the location.
    question : str
        The question associated with the location.
    options : list[AnswerOption]
        A list of answer options for the question.
    """

    name: str
    latitude: float
    longitude: float
    question_type: QuestionType
    question: str
    answer: list[AnswerOption]
    image: str
    dont_know_answer: AnswerOption | None = None

    @property
    def coordinates(self) -> tuple[float, float]:
        """Get the coordinates of the location."""
        return self.latitude, self.longitude
