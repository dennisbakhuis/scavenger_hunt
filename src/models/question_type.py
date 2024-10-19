"""Types of questions that can be associated with a location."""
from enum import Enum


class QuestionType(str, Enum):
    """The type of question associated with a location."""

    MultipleChoice = "multiple choice"
    OpenQuestion = "open question"
