"""Model for an answer option in a question."""
from pydantic import BaseModel


class AnswerOption(BaseModel):
    """
    Represents an answer option for a question.

    Parameters
    ----------
    option : str
        The text of the answer option.
    score : int
        The score associated with selecting this option.
    """

    option: str
    score: int
