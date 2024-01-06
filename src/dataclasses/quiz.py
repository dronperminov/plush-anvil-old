from dataclasses import dataclass
from datetime import datetime


@dataclass
class Quiz:
    name: str
    short_name: str
    date: datetime
    time: str
    place: str
    organizer: str
    description: str
    cost: int
    position: int
    teams: int

    @classmethod
    def from_dict(cls: "Quiz", data: dict) -> "Quiz":
        return Quiz(
            data["name"],
            data["short_name"],
            data["date"],
            data["time"],
            data["place"],
            data["organizer"],
            data["description"],
            data["cost"],
            data["position"],
            data["teams"]
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "short_name": self.short_name,
            "date": self.date,
            "time": self.time,
            "place": self.place,
            "organizer": self.organizer,
            "description": self.description,
            "cost": self.cost,
            "position": self.position,
            "teams": self.teams
        }
