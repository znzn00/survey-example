from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from datetime import datetime


class Roles(Enum):
    SYSADMIN = 0
    ORGANIZATION_ADMIN = 1
    RESEARCHER = 2
    ANALYST = 3


class Organization:
    id: int
    name: str
    description: Optional[str]


@dataclass
class User:
    id: int
    role: Roles
    name: str
    username: str
    password: str
    organization_id: Optional[int] = None


class QuestionType(Enum):
    TEXT = 0
    NUMBER = 1
    CHECKBOX = 2
    PERCENTAGE = 3
    SLIDE = 4
    RATIO_SELECT = 5
    MENU_SELECT = 6
    MULTI_MENU_SELECT = 7


class Answer:
    id: int
    name: str
    description: Optional[str]
    order: int


class AttributeType(Enum):
    MIN_VALUE = 0
    MAX_VALUE = 1
    MIN_SELECT = 2
    MAX_SELECT = 3
    MIN_LABEL = 4
    MAX_LABEL = 5


class Attribute:
    type: AttributeType
    value: str


class Question:
    id: int
    type: QuestionType
    header: str
    description: Optional[str]
    attributes: List[Attribute]
    answers: Optional[List[Answer]]

class ResultAnswer:
    question: Question
    answer: Answer | str | float

class Result:
    id: int
    survey_id: int
    ip: str
    submitted_date: datetime
    answers: List[ResultAnswer]

class Survey:
    id: int
    user: Optional[User]
    organization: Optional[Organization]
    title: str
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]