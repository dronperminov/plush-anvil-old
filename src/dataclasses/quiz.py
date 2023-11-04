from dataclasses import dataclass
from datetime import datetime


@dataclass
class Quiz:
    name: str
    date: datetime
    time: str
    place: str
    description: str
    cost: int
