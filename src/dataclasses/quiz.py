import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from src.constants import SMUZI_POSITION_TO_SCORE


@dataclass
class Quiz:
    name: str
    short_name: str
    date: datetime
    time: str
    place: str
    organizer: str
    description: str
    category: str
    cost: int
    position: int
    teams: int
    players: int
    participants: List[dict]

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
            data["category"],
            data["cost"],
            data["position"],
            data["teams"],
            data["players"],
            data["participants"]
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
            "category": self.category,
            "cost": self.cost,
            "position": self.position,
            "teams": self.teams,
            "players": self.players,
            "participants": self.participants
        }

    def to_inline_title(self) -> str:
        return f"{self.date.day:02d}.{self.date.month:02d} {self.name}"

    def to_inline_description(self) -> str:
        weekday_description = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"][self.date.weekday()]
        return f"{weekday_description}, {self.time}\n{self.place} {self.cost} руб."

    def to_poll_title(self, places: Dict[str, dict]) -> str:
        header_date = self.__get_header_date()
        header_place = f'{self.place} (м. {places[self.place]["metro_station"]}) {self.cost} руб.'
        poll_title = f"{header_date} {self.name}. {header_place}"

        if len(poll_title) >= 240:
            poll_title = f"{header_date} {self.__clear_short_name()}. {header_place}"

        return poll_title

    def to_poll_option(self, places: Dict[str, dict]) -> str:
        header_date = self.__get_header_date()
        header_place = f'{self.place} (м. {places[self.place]["metro_station"]})'
        poll_option = f"{header_date} {self.name}. {header_place}"
        short_name = self.__clear_short_name()

        if len(poll_option) > 100:
            poll_option = f"{header_date} {short_name}. {header_place}"

        if len(poll_option) > 100:
            poll_option = f"{header_date} {short_name}. {self.place}"

        if len(poll_option) > 100:
            max_len = 95 - len(header_date) - len(self.place)
            poll_option = f"{header_date} {short_name[:max_len]}... {self.place}"

        return poll_option

    def smuzi_rating(self) -> int:
        if self.date < datetime(2024, 1, 1) or self.position == 0 or self.organizer != "Смузи":
            return 0

        return SMUZI_POSITION_TO_SCORE.get(self.position, 50)

    def is_win(self) -> bool:
        return self.position == 1

    def is_prize(self) -> bool:
        return 2 <= self.position <= 3

    def is_top10(self) -> bool:
        return 4 <= self.position <= 10

    def is_last(self) -> bool:
        return self.position == self.teams and self.position > 0

    def __get_header_date(self) -> str:
        weekday = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][self.date.weekday()]
        return f"{self.date.day:02d}.{self.date.month:02d} {weekday} {self.time}"

    def __clear_short_name(self) -> str:
        short_name = re.sub("<br>", " ", self.short_name)
        short_name = re.sub(r"\s+", " ", short_name)
        short_name = re.sub(r"</?span[^>]*?>", "", short_name)
        return short_name
