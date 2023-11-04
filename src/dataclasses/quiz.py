from datetime import datetime
from dataclasses import dataclass


@dataclass
class Quiz:
    name: str
    date: datetime
    time: str
    place: str
    description: str
    cost: int
