import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict


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

    def to_inline_title(self) -> str:
        name = re.sub(r"\.$", "", self.name)
        return f"{self.date.day:02d}.{self.date.month:02d} {name}"

    def to_inline_description(self) -> str:
        weekday_description = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"][self.date.weekday()]
        return f"{weekday_description}, {self.time}\n{self.place} {self.cost} руб."

    def to_poll_title(self, places: Dict[str, dict]) -> str:
        name, short_name = re.sub(r"\.$", "", self.name), re.sub(r"\n+", " ", self.short_name)
        weekday = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][self.date.weekday()]

        header_date = f"{self.date.day:02d}.{self.date.month:02d} {weekday} {self.time}"
        header_place = f'{self.place} (м. {places[self.place]["metro_station"]}) {self.cost} руб.'

        poll_title = f"{header_date} {name}. {header_place}"

        if len(poll_title) >= 240:
            poll_title = f"{header_date} {short_name}. {header_place}"

        return poll_title
