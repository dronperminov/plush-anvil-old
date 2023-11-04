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

    @classmethod
    def from_dict(cls: "Quiz", data: dict) -> "Quiz":
        return Quiz(data["name"], data["date"], data["time"], data["place"], data["description"], data["cost"])

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "date": self.date,
            "time": self.time,
            "place": self.place,
            "description": self.description,
            "cost": self.cost
        }
